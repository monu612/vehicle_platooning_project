## 2026-08-12 - [Pathfinding Optimization]
**Learning:** Pre-computing dynamic routes in networkx on the static base topology and verifying edge existence at runtime is dramatically faster than constantly evaluating dynamic network simple paths per iteration.
**Action:** Always consider pre-computing and filtering valid subgraph paths on static base networks to reduce unnecessary computations inside a tight loop when node topologies remain static.
