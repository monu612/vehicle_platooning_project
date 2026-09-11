## 2024-05-14 - Built-in Function Call Overhead
**Learning:** Python's built-in `min()` and `max()` functions have significant function call overhead when used inside extremely tight loops (like iterating over edges in path scoring or pheromone clamping).
**Action:** Replace `min()` and `max()` inside helper functions like `_edge_metric` and `_clamp_pheromone` with `if/else` statements or inline ternary operations to achieve cleaner performance gains without sacrificing code readability.
