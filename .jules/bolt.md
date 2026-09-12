## 2024-05-15 - [Avoid repeated graph path calculations for dynamic graphs]
**Learning:** In a dynamic graph simulation with stationary nodes but dynamic edges (reliability, failures), calling `nx.all_simple_paths` on the dynamically mutated graph at every path selection step is a significant performance bottleneck.
**Action:** Precompute the simple paths on the pristine static base topology *before* dynamic mutations occur. During selection, filter these precomputed paths by checking if all required consecutive edges still exist in the current mutated graph.
