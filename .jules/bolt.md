## 2024-05-24 - Precomputing NetworkX Simple Paths for Dynamic Graphs
**Learning:** `nx.all_simple_paths` relies on a DFS generator which is highly expensive when called in tight loops (e.g., for every ant, for every destination, on every frame). It is a significant bottleneck for ACO simulations.
**Action:** For pathfinding on a dynamic networkx graph, precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them by verifying every consecutive edge exists using `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`.
