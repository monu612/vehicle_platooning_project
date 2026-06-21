## 2024-06-21 - NetworkX Dynamic Graph Pathfinding Bottleneck
**Learning:** Calling `nx.all_simple_paths` on every iteration of a dynamic simulation is a major performance bottleneck because it rebuilds paths from scratch even though only edge weights and presence change.
**Action:** Precompute paths once on the pristine, static base topology *before* the simulation loops start. During simulation iterations, pass these precomputed paths and filter them simply using `G.has_edge(u, v)`.
