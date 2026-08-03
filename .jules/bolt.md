## 2024-05-24 - Precomputing static paths for dynamic graphs
**Learning:** In simulations involving dynamic graphs with changing edge attributes and link failures where nodes remain static, repeatedly calculating `nx.all_simple_paths` per iteration is a massive bottleneck.
**Action:** Precompute paths on the pristine static baseline topology before iterations start, and filter/validate these precomputed paths inside the iteration loop (e.g. using `G.has_edge`) instead of running expensive graph traversal algorithms repeatedly.
