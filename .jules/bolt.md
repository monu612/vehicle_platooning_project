## 2025-02-28 - Precomputed static paths for dynamic graph optimization
**Learning:** Precomputing simple paths on the static base topology before any dynamic link failures significantly improves performance (approx 2.5x speedup) when evaluating paths on a dynamically changing networkx graph. We just need to check if edges still exist `G.has_edge()` during path selection instead of fully re-computing paths at each step.
**Action:** When working with changing networkx graph topologies, precompute and filter valid paths instead of running full shortest-path algorithms inside the dynamic loop.
