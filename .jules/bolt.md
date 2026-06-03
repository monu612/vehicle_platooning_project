## 2024-05-24 - Precomputing NetworkX Simple Paths for Dynamic Graphs

**Learning:** When simulating dynamically failing networks (like dropping random edges with link failures), continuously calling `nx.all_simple_paths` on temporarily degraded subgraphs incurs high overhead (`_all_simple_edge_paths` dominates execution time). Since the nodes and maximum possible edges (topology) remain static across iterations, computing all possible valid routes up to a cutoff once is faster.

**Action:** Precompute paths on the static base topology and filter them based on the current subgraph using simple checks like `G.has_edge(u, v)` rather than repeatedly recalculating `nx.all_simple_paths` during each simulation iteration.
