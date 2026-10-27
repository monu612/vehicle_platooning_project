
## 2026-10-27 - Caching Dynamic Networkx Generator Algorithms
**Learning:** For pathfinding on dynamic networkx graphs, never cache generator-based algorithms (like nx.all_simple_paths) directly onto the dynamically mutating graph object. Instead, fully pre-populate the paths cache using the pristine static base topology before the simulation loop begins, and filter them dynamically per iteration by verifying that every consecutive edge still exists.
**Action:** Pre-compute paths on the static topology and filter them inside dynamic loops.
