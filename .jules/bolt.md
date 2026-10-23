## 2026-05-27 - [NetworkX Path Search Optimization]
**Learning:** `nx.all_simple_paths` is computationally expensive to run repeatedly, especially in tight loops where the graph topology only changes slightly (e.g., edges being removed probabilistically).
**Action:** Implemented memoization for `nx.all_simple_paths` using a frozenset of graph edges as part of the cache key. This significantly reduces redundant pathfinding computations, cutting simulation time by over 50%.
