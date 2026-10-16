## 2024-10-16 - Replacing min/max with if/else for performance
**Learning:** Python's built-in `min()` and `max()` functions introduce significant function call overhead when used inside extremely tight loops, such as graph edge evaluations.
**Action:** Replace `min()` and `max()` with simple `if/else` blocks or ternary operators in critical path functions to improve execution speed without sacrificing readability.
