## 2024-05-19 - Precomputing valid paths on static topology instead of dynamically discovering them

**Learning:** Finding simple paths (`nx.all_simple_paths`) in a dynamic graph inside every single simulation iteration across every route destination is extremely slow. We learned that the graph mutations are limited to edge/weight removals and updates. The set of valid simple paths will only shrink from the baseline paths based on the base graph's topology. Lazy initialization wouldn't work when paths are temporarily broken and recovered.

**Action:** Pre-compute all simple paths on the pristine static base topology *before* any dynamic mutations occur. Filter the precomputed paths dynamically in the `select_path` function by quickly verifying if all consecutive edges currently exist in the networkx graph structure.
