## 2024-05-24 - Inline max() for performance
**Learning:** Replacing Python's built-in `max()` with a ternary operator in a frequently called function (`_edge_metric`) avoids function call overhead and significantly improves performance in tight loops for this codebase.
**Action:** Always consider replacing basic built-in functions like `max()` or `min()` with ternary operators when they are bottlenecks in critical path functions.
