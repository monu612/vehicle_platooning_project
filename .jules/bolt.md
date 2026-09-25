## 2026-09-25 - Replace built-in min/max with if/else in tight loops
**Learning:** Built-in `min()` and `max()` functions add significant overhead when called tens of thousands of times in inner loops. A benchmark showed that a simple `if`/`elif` block for bounding a value executes in 0.077s compared to 0.645s for `max(min, max(value, min))`.
**Action:** In critical performance paths, particularly tight loops, avoid Python's built-in `min`/`max` functions in favor of `if/else` blocks or inline ternaries to eliminate function call overhead.
