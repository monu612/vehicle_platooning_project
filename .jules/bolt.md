## 2025-02-28 - Bottleneck in networkx pathfinding on dynamic graphs
**Learning:** `nx.all_simple_paths` is a massive performance bottleneck when called repeatedly on a dynamically mutating graph during simulation iterations. The CPU time is mostly spent recomputing paths from scratch.
**Action:** For pathfinding on dynamic topologies with static nodes, precompute all simple paths on the pristine static base topology once, and then simply filter those precomputed paths using `G.has_edge(u, v)` during dynamic iterations.
