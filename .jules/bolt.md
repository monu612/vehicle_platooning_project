## 2024-05-24 - [Avoid min()/max() in tight loops]
**Learning:** Python's built-in `min()` and `max()` functions have a surprisingly high function call overhead when used in tight loops, such as evaluating metrics for every single edge in a graph (e.g., in Ant Colony Optimization path scoring).
**Action:** Replace `min()` and `max()` calls inside heavily executed inner loops with inline ternary operators (`val if val > min_val else min_val`) or `if/elif/else` blocks to significantly reduce execution time without sacrificing much readability.
