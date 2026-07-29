## 2025-02-23 - Precompute static paths for ACO dynamic graph
**Learning:** Pathfinding (like nx.all_simple_paths) on dynamically mutating graphs is extremely slow and a major bottleneck. Precomputing paths on the pristine static graph and dynamically verifying edge existence during simulation provides a massive speedup while retaining exact correctness.
**Action:** Always precompute simple paths on the base topology and filter them by verifying consecutive edges (e.g., all(G.has_edge(u, v) for u, v in zip(path, path[1:]))) instead of recomputing paths on mutated graphs.
