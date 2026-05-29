## 2024-05-29 - [Graph Path Precomputation]
**Learning:** [Repeatedly calling `nx.all_simple_paths` on a graph that only loses edges is a major performance bottleneck in simulation loops. Precomputing the paths once and filtering them based on remaining edges is significantly faster.]
**Action:** [When simulating link failures on a static node topology, precompute paths upfront and dynamically filter them rather than searching the graph from scratch on every iteration.]
