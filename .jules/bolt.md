## 2024-05-18 - Optimize max/min overhead in tight loops
**Learning:** Python's built-in `max()` and `min()` functions have overhead due to C-level function call and argument unpacking. In computationally heavy inner loops (like the `_edge_metric` function in an ACO algorithm), this overhead becomes a bottleneck.
**Action:** Replace `max()` and `min()` with inline `if/else` conditional expressions (`val if val > min_val else min_val`) to significantly reduce execution time without changing behavior.
