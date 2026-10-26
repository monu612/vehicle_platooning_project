
## 2026-10-26 - Precomputing simple paths in dynamic topology
**Learning:** For pathfinding on dynamic networkx graphs, repeatedly querying `nx.all_simple_paths` directly on a dynamically mutating graph object within a loop is a massive performance bottleneck because it rebuilds paths from scratch on every iteration despite the underlying nodes mostly remaining static.
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and pass them into the inner loops. Filter them dynamically per iteration by verifying that every consecutive edge in the path still exists on the mutated graph, rather than caching on the graph itself (which causes stale caches).
