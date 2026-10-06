## 2024-05-18 - Built-in max function overhead in tight loops
**Learning:** The standard library `max()` function has significant overhead when called repeatedly inside tight loops like `_edge_metric`, which processes thousands of edges. An inline ternary condition is significantly faster.
**Action:** When writing small wrapper functions that execute inside high-frequency loops (like graph processing or ant colony simulations), use inline ternary checks (e.g., `val if val > min_val else min_val`) instead of standard `max()` or `min()` functions to minimize function call overhead.
