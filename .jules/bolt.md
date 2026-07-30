## 2026-07-30 - NetworkX Pathfinding Optimization on Dynamic Graphs
**Learning:** Dynamically calling `nx.all_simple_paths` in a tight loop on a NetworkX graph that only experiences edge removal is a massive performance bottleneck.
**Action:** Precompute simple paths on the pristine static base topology before any dynamic mutations occur, and filter them during execution by verifying every consecutive edge exists using `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`. Do not use lazy initialization during a disrupted state, as it permanently omits paths that are temporarily broken.
