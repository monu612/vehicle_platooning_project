## 2024-05-24 - NetworkX path finding bottleneck
**Learning:** Calling `nx.all_simple_paths` inside the `select_path` loop in the ACO simulation is a massive bottleneck. The graph topology is relatively static (only edges drop sometimes, nodes and max potential edges are constant). Computing simple paths repeatedly from scratch takes up the majority of the simulation time (~50% of the runtime).
**Action:** Pre-compute and cache all simple paths for the maximum topology. During the simulation, simply filter the cached paths to only include those whose edges currently exist in `G_temp`.
