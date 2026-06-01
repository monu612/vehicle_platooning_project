## 2024-05-15 - Graph Path Precomputation
**Learning:** For pathfinding on dynamic networkx graphs, repeatedly recalculating `nx.all_simple_paths` on temporarily degraded subgraphs is a major performance bottleneck.
**Action:** Precompute simple paths on the static base topology once, and filter those precomputed paths using `G.has_edge()` during iterations instead of calling `all_simple_paths` each time.
