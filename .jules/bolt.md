## 2023-10-24 - Inline conditionals inside helper functions
**Learning:** Python's built-in `max()` and `min()` functions add measurable overhead when called millions of times inside tight loops (like ACO pheromone updates).
**Action:** Replaced `max()` and `min()` with simple `if/else` blocks or inline ternary operators inside the frequently called `_edge_metric` and `_clamp_pheromone` helper functions, achieving significant speedup without sacrificing code readability.
