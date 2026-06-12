## 2024-03-24 - Precomputing Graph Paths
**Learning:** For pathfinding on dynamic networkx graphs, repeatedly computing paths using `nx.all_simple_paths` is a significant performance bottleneck due to generator creation overhead when edge removals don't change the set of simple paths very often.
**Action:** Precompute paths on the initial static topology, then dynamically filter those paths based on current graph connectivity (`G.has_edge(u, v)`) to greatly improve pathfinding performance.
