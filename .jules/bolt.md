## 2026-10-23 - Avoid generator overhead with dynamic path caching
**Learning:** For pathfinding on dynamic networkx graphs, repeatedly invoking generator-based algorithms (like `nx.all_simple_paths`) per iteration on mutated graphs is a significant bottleneck. However, we cannot directly cache generators on the dynamic graph object.
**Action:** Precompute simple paths on the pristine static base topology before any mutations occur, and filter them dynamically per iteration by verifying that every consecutive edge still exists.
