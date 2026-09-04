## 2026-09-04 - Inlining _edge_metric and built-in functions
**Learning:** Python function calls (`_edge_metric`, `min`, `max`, `math.isfinite`) have a massive overhead when called per edge inside tight loops (like `_path_score`).
**Action:** Always inline dictionary lookups (`float(edge.get("key", default))`), `min`/`max` with ternary operations (`val if val > min_val else min_val`), and check for finiteness with `!= float('inf')` to boost tight loop performance drastically.
