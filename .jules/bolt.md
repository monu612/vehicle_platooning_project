## 2024-08-15 - [Precomputing paths in dynamic NetworkX graph]
**Learning:** Calling `nx.all_simple_paths` repeatedly inside an inner simulation loop on a dynamically mutating graph (where edge attributes change and edges are temporarily removed) causes massive profiling overhead.
**Action:** Precompute all simple paths once on the initial, pristine topology graph before the simulation loop. During path selection, filter these precalculated paths by verifying every consecutive edge still exists in the mutated graph using `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`.
