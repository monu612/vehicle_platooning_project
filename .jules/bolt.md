## 2024-05-24 - Performance Optimizations
**Learning:** Python's built-in `min()` and `max()` functions have significant function call overhead when used inside tight loops for simple scalar comparisons.
**Action:** Replace `min()` and `max()` with simple inline ternary operations (or `if/else` blocks inside small helpers) inside tight loops (like graph traversal or path scoring) to reduce overhead, while avoiding unreadable nesting.
