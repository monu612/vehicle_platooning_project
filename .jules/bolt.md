## 2024-05-14 - Python Built-in Overhead in Tight Loops
**Learning:** Calling built-in math functions like `min()` and `max()` inside extremely tight algorithmic loops (like ant colony pheromone updates in `aco.py`) incurs noticeable function call and argument-unpacking overhead in CPython compared to simple control flow.
**Action:** Replace `min()` and `max()` with inline ternary operations (e.g., `val if val > min_val else min_val`) or explicit `if/else` blocks in performance-critical Python paths that don't use `numpy` to reduce execution time without sacrificing readability.
