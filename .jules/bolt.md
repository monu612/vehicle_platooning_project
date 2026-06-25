## 2024-05-18 - Precomputing Simple Paths on Dynamic Graph

**Learning:** Re-computing simple paths dynamically using networkx (`nx.all_simple_paths`) during every iteration of an ACO simulation heavily impacts performance, as the topology is disrupted (edges removed/modified). In this case, `nx.all_simple_paths` was the bottleneck. Computing these simple paths on the pristine static base topology *before* the dynamic mutations, and filtering those pre-computed paths to exclude ones with missing edges (`G.has_edge`) in the mutated graph is significantly faster (speed up from ~1.6s to ~0.25s for 200 iterations).

**Action:** Whenever iterating and pathfinding over a dynamically mutating networkx graph where nodes remain static and only edges change/fail, pre-compute all possible simple paths on the original topology once, and dynamically filter them using `has_edge` during mutations.
