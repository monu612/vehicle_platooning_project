## 2024-05-15 - [Python builtin function overhead]
**Learning:** Using Python's built-in `min()` and `max()` functions inside extremely tight loops incurs significant function call overhead compared to simple conditional blocks or ternary operators.
**Action:** Break nested ternaries or `min()`/`max()` calls into simple `if/else` blocks to achieve the same performance gain cleanly without sacrificing readability when optimizing tight loops.
