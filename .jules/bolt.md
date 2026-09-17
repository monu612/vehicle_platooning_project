## 2026-09-17 - [Optimized min/max in tight loops]
**Learning:** Python's built-in `min()` and `max()` functions have significant function call overhead when used in tight loops (like those in network pathfinding or ACO).
**Action:** Replace `min()` and `max()` with inline conditionals or ternary operators in critical performance paths to improve execution time without sacrificing much readability.
