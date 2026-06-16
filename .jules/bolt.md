
## 2024-06-16 - Precomputing paths on static topology for dynamic graphs
**Learning:** For pathfinding on dynamic NetworkX graphs where only edges mutate, precomputing paths on the pristine static topology and filtering by edge existence is significantly faster than recalculating paths from scratch using `nx.all_simple_paths`.
**Action:** Always precompute static paths and validate against dynamic edges when simulating node-static networks.
