## 2024-03-24 - Inline wrapper methods for performance
**Learning:** Found an edge metric lookup wrapper `_edge_metric(edge, key, default)` that is heavily used in hot loops in `aco.py` and causes Python function overhead.
**Action:** Inline it or rewrite the tight loops to access dict and max directly to skip function call overhead.
