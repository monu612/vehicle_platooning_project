## 2026-08-26 - Optimize tight inner loop with inlining and index-based iteration
**Learning:** Inlining dictionary `.get()` logic and replacing `zip(path, path[1:])` with index-based iteration significantly speeds up python loops by avoiding list slicing and wrapper function call overhead in tight pathfinding logic like `_path_score`.
**Action:** Apply this optimization to tight inner loops iterating over consecutive elements in a sequence, especially when wrapper functions are used heavily.
