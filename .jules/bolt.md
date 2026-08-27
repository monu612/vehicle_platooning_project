## 2024-05-18 - Avoid zip(path, path[1:]) in hot loops

**Learning:** Replacing `zip(path, path[1:])` with `range(len(path) - 1)` in the inner loops (`_path_score`, `update_pheromone`, `_path_latency`) significantly improves performance by avoiding the overhead of list slicing and tuple unpacking in Python.

**Action:** Whenever iterating over consecutive items in a list (like edges in a path) inside a performance-critical loop, use index-based access with `range(len(path) - 1)` instead of `zip()`.

## 2024-05-18 - Inline wrapper functions for dictionary lookups

**Learning:** The `_edge_metric` and `_clamp_pheromone` wrapper functions introduce significant Python function call overhead when executed hundreds of thousands of times per simulation run. Inlining the dictionary `.get()` with explicit bounds (e.g., `max(float(edge.get("weight", 1.0)), 1e-9)`) provides a major speedup.

**Action:** Avoid abstracting dictionary `.get()` operations with fallback values into helper functions when they are called in tight loops. Inline the logic directly where it's needed.

## 2024-05-18 - Precompute paths before network mutation

**Learning:** Re-running `nx.all_simple_paths` on a dynamically mutating graph every iteration is incredibly slow. Precomputing the paths on the pristine master graph once, and then simply filtering the precomputed list based on `G.has_edge` during the simulation iteration is over 20x faster.

**Action:** For pathfinding in dynamically disrupted topologies where the nodes are static and only edges change, always precompute the paths on the base topology and filter them dynamically rather than re-running the pathfinding algorithm.
