## 2023-10-27 - [NetworkX Generator Cache Optimization]
**Learning:** [For pathfinding on dynamic networkx graphs, calling generator-based algorithms like `nx.all_simple_paths` repeatedly on the mutating graph in a tight loop is highly inefficient. Caching them onto the dynamically mutating graph object is an anti-pattern as it causes stale caches.]
**Action:** [Fully pre-populate the paths cache using the pristine static base topology *before* the simulation loop begins, and filter them dynamically per iteration by verifying that every consecutive edge still exists.]
