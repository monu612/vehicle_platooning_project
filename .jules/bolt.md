## 2026-06-26 - Precompute simple paths on static topology
**Learning:** For pathfinding on the dynamic networkx graph, `nx.all_simple_paths` is computationally expensive to call repeatedly inside loops where graph attributes and topology change (dynamic mutations).
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them using `G.has_edge()` during each simulation step. This is much faster and avoids lazy initialization pitfalls.
