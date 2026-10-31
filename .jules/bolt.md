## 2024-11-01 - ACO Pathfinding Caching
**Learning:** For pathfinding on dynamic networkx graphs, never cache generator-based algorithms directly onto the dynamically mutating graph object, as it causes stale caches, ignores cutoff constraints, and risks memory exhaustion.
**Action:** Fully pre-populate the paths cache using the pristine static base topology before the simulation loop begins, and filter them dynamically per iteration by verifying that every consecutive edge still exists.
