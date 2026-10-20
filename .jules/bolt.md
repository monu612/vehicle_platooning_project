## 2024-10-20 - Inline conditional overhead
**Learning:** Built-in `min()` and `max()` functions in Python introduce noticeable function call overhead when used inside tight loops (like graph edge metric calculations in ACO). Replacing them with simple `if`/`else` blocks significantly speeds up performance.
**Action:** For extremely frequent mathematical bounds checking in generic wrappers, prefer explicit inline conditionals `if val < limit: return limit else: return val` over built-in `max()` or `min()`, while keeping it clean to preserve readability.
