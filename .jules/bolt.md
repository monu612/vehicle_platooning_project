## 2026-11-06 - Pre-populating Paths for Dynamic Graphs
**Learning:** For pathfinding on dynamic networkx graphs, caching generator-based algorithms (like `nx.all_simple_paths`) dynamically during simulation can result in missing paths or excessive overhead. Calling `nx.all_simple_paths` repeatedly inside the simulation loop per iteration is slow.
**Action:** Fully pre-populate the paths cache using the pristine static base topology *before* the simulation loop begins. Inside the loop, filter the paths dynamically per iteration by verifying that every consecutive edge still exists.
