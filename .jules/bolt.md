## 2026-09-20 - [Precomputing Paths on Dynamic Topologies]
**Learning:** In a dynamically changing graph environment with frequent node/edge failures, performing pathfinding (e.g., `nx.all_simple_paths`) during every iteration on the perturbed graph is a major bottleneck.
**Action:** Precompute paths once on the pristine static topology before dynamic failures occur, and then efficiently filter this cached list in each iteration to only include paths where all edges currently exist.
