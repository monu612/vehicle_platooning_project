## 2026-07-13 - [Precomputing paths]
**Learning:** For pathfinding on the dynamic networkx graph, precomputing simple paths on the pristine static base topology *before* any dynamic mutations occur, and filtering them by verifying every consecutive edge exists is a highly effective optimization, cutting simulation time roughly in half.
**Action:** Use precomputed paths on static topologies where edges only fail, rather than recalculating them dynamically.
