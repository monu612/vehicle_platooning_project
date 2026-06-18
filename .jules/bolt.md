## 2024-06-11 - Precompute simple paths for dynamic networkx graphs
**Learning:** For pathfinding on dynamic networkx graphs (where nodes are static but edges fail/recover), `nx.all_simple_paths` gets expensive if re-run per tick on mutated topologies.
**Action:** Precompute simple paths on the pristine static base topology before any mutations occur, and filter them using `G.has_edge(u, v)` during the simulation instead of recomputing from scratch.
