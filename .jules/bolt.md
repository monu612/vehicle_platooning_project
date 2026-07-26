## 2024-07-26 - Precompute NetworkX Simple Paths for Dynamic Graphs
**Learning:** Finding simple paths (`nx.all_simple_paths`) repeatedly on a dynamic graph is a major performance bottleneck due to continuous recomputations.
**Action:** Precompute paths on the pristine static topology before mutations begin, then dynamically filter them for validity (by checking if every edge in the path exists) during simulation iterations to avoid expensive recomputations while handling missing edges.
