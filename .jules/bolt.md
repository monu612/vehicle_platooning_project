
## 2024-05-18 - Precomputing Simple Paths in Dynamic NetworkX Graphs
**Learning:** Calling `nx.all_simple_paths` during a hot loop on a dynamic graph that represents link failures is exceptionally slow and scales poorly. In an ACO simulation where nodes are constant but edges drop, `nx.all_simple_paths` accounts for a vast majority of the execution time.
**Action:** Precompute paths on the static baseline graph before starting the simulation loop. Inside the loop, quickly filter these valid precomputed paths using `G.has_edge(u, v)` instead of recalculating all simple paths from scratch.
