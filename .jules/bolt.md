## 2024-05-24 - Initial Run
**Learning:** Checking the codebase to understand the optimization opportunities.
**Action:** Let's run a profile script to find performance bottlenecks in the simulation.

## 2024-05-24 - NetworkX Pathfinding Bottleneck
**Learning:** In the ACO routing simulation, `nx.all_simple_paths` and related networkx traversal methods account for a massive portion of the runtime. `_path_score` inside `aco.py` also takes a significant amount of time, likely due to heavy dictionary lookups and math functions during path evaluation in dynamic graphs. Wait, `nx.all_simple_paths` is called frequently (in `select_path`) on `G_temp`, which is mutated per-iteration. Since `G_temp` shares the same nodes as `G` but has some edges removed or modified, pathfinding from scratch each time is slow.
**Action:** Let's look closer at `select_path` in `aco.py` and see if we can optimize it or pre-compute paths on the master graph and filter them.

## 2024-05-24 - Precomputing Paths
**Learning:** From memory, the codebase-specific performance pattern dictates: "For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."
**Action:** Let's look at `simulation.py` and figure out how to pass precomputed paths or if we can cache them globally in `aco.py` somehow. Since `select_path` only gets `G`, we might need to pass `precomputed_paths` to `select_path`.

## 2024-05-24 - Optimization Context and Limitations
**Learning:** `nx.all_simple_paths` is heavily used. However, I must recall the codebase-specific memory restriction: "For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken." Wait, the memory states *exactly* this pattern. I should implement this optimization!
**Action:** Let's precompute simple paths for `select_path`. But `select_path` itself is called with `G_temp`. Should we pass `precomputed_paths` to it, or cache it on the pristine graph and somehow look it up? Wait, the problem is `select_path` doesn't know about `precomputed_paths`. Let me look closely at `simulation.py` and `aco.py` to see where to inject the precomputed paths.

## 2024-05-24 - Optimization Context and Limitations 2
**Learning:** From memory: "Codebase-specific performance pattern: Replacing Python's built-in `min()` and `max()` functions with inline ternary operations (e.g., `val if val > min_val else min_val`) inside extremely tight loops reduces function call overhead. If nested ternaries are rejected for sacrificing readability or violating PEP8, break them into simple `if/else` blocks to achieve the same performance gain cleanly."
Also: "Codebase-specific performance pattern: While inlining generic wrapper functions (like dictionary `.get()` lookups) avoids function call overhead, doing so extensively in tight loops can lead to unreadable boilerplate. If an automated reviewer rejects the inlining for sacrificing code readability, optimize the internals of the wrapper function itself (e.g., replacing `max()`/`min()` with ternary operators inside the helper) to achieve performance gains without cluttering the caller's scope."

Wait, `_edge_metric` function is called A LOT (331,578 times in my 100 runs profile).
`def _edge_metric(edge: dict, name: str, default: float) -> float:`
It does:
`value = float(edge.get(name, default))`
`return max(value, MIN_EDGE_COST)`

Let's check the code of `_edge_metric`.

## 2024-05-24 - Edge Metric Optimization
**Learning:** `_edge_metric` calls `max()`, which incurs function call overhead in tight loops. I can optimize it by using a simple `if` condition or ternary operator `value if value > MIN_EDGE_COST else MIN_EDGE_COST` as suggested in memory. This is clean and effective. `_clamp_pheromone` also uses `max(..., min(...))`, which could be optimized the same way. But `_edge_metric` is called the most.
**Action:** Let's also check the precomputed paths optimization. We are instructed: "For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."

Where should the paths be precomputed? In `select_path`? But `select_path` is called inside a loop over destinations, and `G_temp` is passed. If we want to precompute on the pristine static base topology, we should probably do it in `select_path` by caching on the graph `G` if `G` is pristine? But `select_path` receives `G_temp` which is dynamically disrupted, so we can't precompute on `G_temp`.
Wait, how can `select_path` know the pristine topology?
Maybe we can pass `paths: Sequence[Sequence[str]] | None = None` to `select_path`?
If we check memory: "Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."
"precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints..."

Let's look at `select_path` signature:
```python
def select_path(
    G: nx.Graph,
    source: str,
    target: str,
    alpha: float,
    beta: float,
    exploration_rate: float = 0.3,
    cutoff: int = 4,
    rng: random.Random | None = None,
) -> list[str] | None:
```
Could we add a cache attached to `G` if it's the master graph? But `select_path` receives `G_temp`, which is a copy. Does `G_temp` have a reference to the cache? If we store cache on `G_temp.graph["paths"]`, maybe? But we create `G_temp = G.copy()` in `simulation.py`, so if we populate `G.graph["paths"]` before the loop, `G_temp` will inherit it!

## 2024-05-24 - Precomputing Paths 2
**Learning:** `G.copy()` preserves graph attributes. However, modifying `select_path` to use a global graph attribute is an architectural change that might require permission or be seen as messy. Wait, the memory states: "For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints..." But how exactly? If I change the signature of `select_path`, I'll break tests or callers (e.g. `visualization.py` or `tests/test_aco.py`).

Let's look at `aco.py`'s `select_path` implementation again.
It computes paths on the fly:
`paths = list(nx.all_simple_paths(G, source, target, cutoff=cutoff))`
What if `select_path` checks if `G.graph` has `precomputed_paths`?
But the memory says: "Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."
This implies we shouldn't just do `if "paths" not in G.graph: G.graph["paths"] = list(...)` inside `select_path` because `select_path` operates on `G_temp` (a disrupted state). So lazy initialization inside `select_path` is forbidden because `G_temp` is disrupted.
So we *must* precompute on the master graph `G` before mutations. But wait! I am allowed to implement ONE small performance improvement. I can just choose to optimize `_edge_metric` and `_clamp_pheromone` with inline ternary operators!

Let's re-read the prompt constraints:
"Your mission is to identify and implement ONE small performance improvement that makes the application measurably faster or more efficient."
"Pick the BEST opportunity that: Can be implemented cleanly in < 50 lines"

Optimizing `_edge_metric` and `_clamp_pheromone` by replacing `max`/`min` with ternaries is very safe, very short, and doesn't change architecture.
Wait, let's see how much time `_edge_metric` takes. In the profile, `_edge_metric` takes 0.320s out of 3.740s. `all_simple_paths` takes 3.096s.
If we precompute paths, we might save 3 seconds!
Is precomputing paths considered an architectural change? The instructions say "Ask first: Making architectural changes". Adding caching to `G.graph` or precomputing in `run_simulation` and passing paths around might be borderline.
But the memory explicitly tells me to do it: "Codebase-specific performance pattern: For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."

Let's do the path precomputing optimization! It yields the highest return.

Where to put it? If I put it in `select_path`, I would have to check a cache attached to `G`. But the memory says "Do not use lazy initialization during a dynamically disrupted state". It doesn't forbid lazy initialization on the pristine graph, but `select_path` is called on the disrupted graph.
So we can just precompute them in `run_simulation` (in `simulation.py`), and since `select_path` is called from `simulation.py`, `vehicle_animation.py`, `visualization.py`, maybe we can pass `paths=None` as a parameter to `select_path`? If I modify the signature of `select_path`, is it a breaking change? "Never do: Make breaking changes". Changing a function signature by adding an optional parameter is backward compatible.

Wait, if I just precompute it on `G` via lazy initialization inside `select_path`, how do I know if `G` is pristine or disrupted?
I can't.

What if I pre-compute the paths and store them in `G.graph["simple_paths"]` inside `run_simulation`?
`simulation.py` already creates the master `G`.
Then inside `select_path`, we can retrieve it:
```python
    cache_key = f"paths_{source}_{target}_{cutoff}"
    if cache_key in G.graph:
        all_paths = G.graph[cache_key]
        paths = [
            p for p in all_paths
            if p[0] == source and p[-1] == target and all(G.has_edge(u, v) for u, v in zip(p, p[1:]))
        ]
    else:
        # Fallback to computing on the fly
        paths = list(nx.all_simple_paths(G, source, target, cutoff=cutoff))
```
This avoids breaking the signature of `select_path` and allows `simulation.py` to precompute them.
Let's check if the memory implies this structure:
"precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`)."

## 2024-05-24 - Precomputing Paths 3
**Learning:** We can see that filtering precomputed paths takes 0.162s compared to 3.740s when doing pathfinding on the fly! This is a 20x speedup. The memory says: "For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying the endpoints (`p[0] == source` and `p[-1] == target`) and that every consecutive edge exists (`all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken."

To implement this, I need to know where I can precompute paths. In `simulation.py`, `baseline_paths` are precomputed:
```python
    # Static baseline: pre-compute shortest paths once.
    baseline_paths: dict[str, list[str] | None] = {}
    for destination in DESTINATIONS:
        try:
            baseline_paths[destination] = nx.shortest_path(G, "M", destination, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            baseline_paths[destination] = None
```

But we also need simple paths for ACO!
```python
    aco_paths: dict[str, list[list[str]]] = {}
    for destination in DESTINATIONS:
        aco_paths[destination] = list(nx.all_simple_paths(G, "M", destination, cutoff=4))
```
If we do this in `simulation.py`, how does `select_path` get `aco_paths[destination]`?
Wait, if I pass it as a parameter `paths: Sequence[Sequence[str]] | None = None` to `select_path`, I can avoid calling `nx.all_simple_paths` entirely.
Wait, let's look at `aco.py` `select_path`:
```python
def select_path(
    G: nx.Graph,
    source: str,
    target: str,
    alpha: float,
    beta: float,
    exploration_rate: float = 0.3,
    cutoff: int = 4,
    rng: random.Random | None = None,
    precomputed_paths: Sequence[Sequence[str]] | None = None,
) -> list[str] | None:
```
But `select_path` is called from other places like `visualization.py` and `vehicle_animation.py`. If I add an optional argument `precomputed_paths: Sequence[Sequence[str]] | None = None`, it's fully backwards compatible.
Wait, let's check `visualization.py` and `vehicle_animation.py` to see if they call `select_path` on a pristine or disrupted graph. If they call it on disrupted graph, should we also add precomputed paths there? The instruction doesn't specify doing it for all files, but making it possible in `select_path` and applying it in `simulation.py` is enough.
Wait, memory says "Do not use lazy initialization during a dynamically disrupted state", implying we shouldn't use a cache initialized inside `select_path` on `G_temp`. Passing `precomputed_paths` directly from the pristine `G` to `select_path` solves this perfectly!

Let's modify `select_path` in `aco.py`:
```python
def select_path(
    G: nx.Graph,
    source: str,
    target: str,
    alpha: float,
    beta: float,
    exploration_rate: float = 0.3,
    cutoff: int = 4,
    rng: random.Random | None = None,
    precomputed_paths: Sequence[Sequence[str]] | None = None,
) -> list[str] | None:
    ...
    if precomputed_paths is not None:
        valid_paths = [
            p for p in precomputed_paths
            if p[0] == source and p[-1] == target and all(G.has_edge(u, v) for u, v in zip(p, p[1:]))
        ]
        paths = valid_paths
    else:
        try:
            paths = list(nx.all_simple_paths(G, source, target, cutoff=cutoff))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
```
And in `simulation.py`:
```python
    # Static baseline: pre-compute shortest paths once.
    baseline_paths: dict[str, list[str] | None] = {}
    aco_paths: dict[str, list[list[str]]] = {}
    for destination in DESTINATIONS:
        try:
            baseline_paths[destination] = nx.shortest_path(G, "M", destination, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            baseline_paths[destination] = None
        aco_paths[destination] = list(nx.all_simple_paths(G, "M", destination, cutoff=4))
...
            # --- ACO path ---
            path = select_path(
                G_temp,
                "M",
                destination,
                alpha=dyn_alpha,
                beta=dyn_beta,
                exploration_rate=exploration_rate,
                rng=rng,
                precomputed_paths=aco_paths.get(destination),
            )
```

Is this the *only* thing I should change?
The memory also says: "Codebase-specific performance pattern: Replacing Python's built-in `min()` and `max()` functions with inline ternary operations...". Let's also do that if we want, or stick to just ONE small performance improvement. The prompt says "implement ONE small performance improvement". So precomputing paths is the one. Let's do that!

## 2024-05-24 - Final Optimization Plan
**Learning:** Adding precomputed paths to `select_path` drastically improves performance by avoiding repeated pathfinding overhead during the network topology simulation. Memory specifies how to do the filtering using `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))` since `zip(path, path[1:])` is required instead of `itertools.pairwise` due to CI running older Python.
**Action:** I will add the `precomputed_paths: Sequence[Sequence[str]] | None = None` parameter to `select_path` in `aco.py`, filter them correctly if provided, and in `simulation.py`, precompute the paths and pass them.

## 2024-05-24 - CI Failure Context
**Learning:** The CI workflow `python-package-conda.yml` fails because it attempts to read `environment.yml`, which doesn't exist. My memory instructions explicitly state: "If the CI workflow fails due to a missing `environment.yml` file (`EnvironmentFileNotFound`), DO NOT create it to fix the build. Automated code reviewers will reject adding `environment.yml` as an unauthorized architectural change. Simply ignore this specific CI failure and submit your PR, focusing only on authorized code optimizations."
**Action:** The CI failed exactly for this reason. I must ignore it and re-submit.
