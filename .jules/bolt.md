## 2026-07-16 - [Precomputing paths for dynamic graphs]
**Learning:** In dynamically changing networkx graphs (edges removed/modified), continuously recalculating `nx.all_simple_paths` on every iteration is a major performance bottleneck. Precomputing paths on the pristine static topology and filtering by verifying consecutive edges (e.g., `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`) avoids the overhead of pathfinding on disrupted states.
**Action:** Precompute paths once and pass them down as an optional argument to route selection functions.
