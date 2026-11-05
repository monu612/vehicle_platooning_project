## 2026-11-05 - Pre-computing paths for dynamic networkx graphs
**Learning:** For pathfinding on dynamic networkx graphs in a simulation loop, lazily invoking `nx.all_simple_paths` on every tick is a major bottleneck because it recalculates paths over the entire graph structure repeatedly, especially since the base topology doesn't change, only edge attributes/existence.
**Action:** Pre-compute the generator outputs into a list using the pristine static base topology *before* the loop, and dynamically filter them per iteration by verifying `G.has_edge(u, v)`.
