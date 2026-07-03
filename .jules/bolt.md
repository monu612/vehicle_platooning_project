
## 2024-05-18 - Precomputing Simple Paths on Dynamic Topologies
**Learning:** In network simulations where link weights/existence fluctuate but node topology remains static (like in `simulation.py`), dynamically recalculating `nx.all_simple_paths` on every iteration per packet is a major performance bottleneck.
**Action:** Instead of repeating expensive pathfinding searches, precompute `nx.all_simple_paths` once on the pristine static graph before the simulation loop, and during path selection simply filter out precomputed paths that contain failed edges using `G.has_edge(u, v)`.
