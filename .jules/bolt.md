## 2026-07-23 - Precompute simple paths on static topology
**Learning:** Pathfinding with networkx on a dynamic topology per iteration is a major bottleneck.
**Action:** Precompute paths on the pristine static topology before mutations occur and filter dynamically based on edge presence during path selection to drastically improve performance.
