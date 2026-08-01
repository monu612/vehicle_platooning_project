## 2024-06-25 - Pathfinding Optimizations

**Learning:** Recomputing pathfinding for dynamic networks (like those built on `networkx`) using deep `nx.all_simple_paths` on a disrupted network each iteration takes a lot of processing time due to internal logic trying to generate paths during simulation permutations.
**Action:** Pre-compute the baseline sets of potential paths on the static, un-perturbed network graph. During simulation permutations with link failures, rather than dynamically asking networkx to generate entirely new potential paths across failing edges, validate the previously pre-computed paths by checking `if all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`. This completely side-steps the overhead of finding paths per-iteration on the altered graph.
