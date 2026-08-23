## 2026-08-23 - Avoid zip memory allocation in graph hot loops
**Learning:** In tight path scoring loops (e.g., `_path_score`), using `zip(path, path[1:])` creates a sliced copy of the list and a zip generator, which incurs significant overhead. Inlining helper functions and using index-based iteration `range(len(path) - 1)` cuts execution time by over 50%.
**Action:** Always prefer index-based iteration `for i in range(len(path) - 1)` over `zip(path, path[1:])` for evaluating sequences of edges in highly-called simulation functions.
