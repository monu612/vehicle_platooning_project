## 2024-06-07 - Precomputing Paths in Dynamic NetworkX Graphs
**Learning:** For pathfinding on a dynamic networkx graph, calling `nx.all_simple_paths` on every route request during simulation loop is highly inefficient.
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them using `G.has_edge()`.
