## 2025-02-03 - Precompute static paths for dynamic graph pathfinding
**Learning:** For pathfinding on the dynamic networkx graph, `nx.all_simple_paths` is heavily bottlenecked during each iteration because it recomputes from scratch.
**Action:** Precompute simple paths on the pristine static base topology before any dynamic mutations occur, and filter them by verifying every consecutive edge exists (e.g., `all(G.has_edge(u, v) for u, v in zip(path, path[1:]))`). Do not use lazy initialization during a dynamically disrupted state, as it permanently omits paths that are temporarily broken.
