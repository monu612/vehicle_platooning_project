## 2024-05-24 - Built-in min/max overhead in Python
**Learning:** Using Python's built-in `min()` and `max()` functions for simple numeric constraints inside tight loops (like pathfinding wrappers) introduces noticeable function call overhead.
**Action:** Replace `min()` and `max()` with simple `if` blocks for numeric bounds in frequently called inner loop helpers to halve execution time.
