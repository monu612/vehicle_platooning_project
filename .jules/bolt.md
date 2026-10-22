## 2023-10-24 - Python Built-in Function Call Overhead in Tight Loops
**Learning:** In tight loops like `_path_score` inside generic algorithms, the function call overhead of Python's built-in `min()` and `max()` inside helper functions like `_edge_metric` and `_clamp_pheromone` causes a measurable performance bottleneck.
**Action:** Replace `min()` and `max()` with simple `if/else` blocks inside frequently called wrapper functions to eliminate the call overhead without cluttering the caller's scope or sacrificing code readability.
