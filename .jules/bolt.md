## 2024-05-24 - Avoiding built-in min/max overhead in tight loops
**Learning:** Using Python's built-in `min()` and `max()` functions in extremely tight loops (like iterating over edges during path selection or pheromone updates) introduces noticeable function call overhead.
**Action:** Replace `min()` and `max()` with simple inline ternary operations (e.g., `val if val > min_val else min_val`) or `if/else` blocks to significantly reduce execution time without significantly impacting readability.
