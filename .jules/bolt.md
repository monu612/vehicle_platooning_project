## 2024-05-24 - Avoid min()/max() in tight loops
**Learning:** Python's built-in `min()` and `max()` functions have notable function call overhead due to argument packing and C-API calls, which becomes a bottleneck inside hot loops like evaluating path scores and updating pheromones in ACO.
**Action:** Replace `min()` and `max()` with inline `if/else` statements for simple numeric comparisons in performance-critical paths to achieve a ~5% speedup without sacrificing readability when documented.
