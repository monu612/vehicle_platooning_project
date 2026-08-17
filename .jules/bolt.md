## 2025-01-01 - Optimization of tight loops
**Learning:** Inlining simple wrapper functions like `_edge_metric` inside hot loops like `_path_score` significantly reduces Python function call overhead.
**Action:** When working with graphs that are evaluated thousands of times, inline dictionary lookups (`.get`) with min/max bounds instead of relying on helper functions.
## 2025-01-01 - Precomputing paths on dynamic graphs
**Learning:** For pathfinding on a dynamic networkx graph with static nodes but changing edges (link failures), repeated calls to `nx.all_simple_paths` are a huge bottleneck.
**Action:** Precompute simple paths on the pristine static base topology before any dynamic mutations occur, and filter them by verifying every consecutive edge exists using `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))` instead of lazy initialization.
