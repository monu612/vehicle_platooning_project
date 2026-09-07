## 2024-05-15 - Inlining wrapper functions and min/max in tight loops
**Learning:** Python function call overhead (`_edge_metric`, `max`, `min`) in tight inner loops (like `_path_score` which is called per path, per edge) dominates execution time in graph routing simulations.
**Action:** Inline dictionary lookups and use ternary operators instead of `min`/`max` in highly executed inner loops.
