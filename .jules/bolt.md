## 2023-11-20 - [Precomputing Dynamic Paths]
**Learning:** For pathfinding on a dynamic networkx graph where only edge attributes change or edges fail (nodes remain static), using `nx.all_simple_paths` on every mutation step is extremely expensive.
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them using `G.has_edge()` during the simulation. This avoids the overhead of path enumeration on every iteration while still ensuring valid paths on the mutated graph.
