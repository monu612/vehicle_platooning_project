## 2024-06-23 - Dynamic graph pathfinding
**Learning:** For pathfinding on the dynamic networkx graph, precompute simple paths on the pristine static base topology before any dynamic mutations occur, and filter them using `G.has_edge()`. Recomputing `nx.all_simple_paths` on every packet transmission is highly redundant as the base topology's nodes never change.
**Action:** Optimize `select_path` in `aco.py` to accept precomputed paths or modify the simulation loop to precompute paths and pass them.
