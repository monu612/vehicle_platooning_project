## 2025-02-17 - [Optimization: Precomputing Simple Paths]
**Learning:** For pathfinding on the dynamic networkx graph, calling `nx.all_simple_paths` repeatedly inside the simulation loop is extremely slow and acts as a significant bottleneck.
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them using `G.has_edge()`. Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken.
