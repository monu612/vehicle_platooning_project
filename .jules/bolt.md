## 2024-05-24 - Tight loop function call overhead
**Learning:** Python's built-in `min()` and `max()` functions introduce significant C-API call overhead when executed hundreds of thousands of times in tight algorithmic loops like ACO path selection.
**Action:** Replace `min()` and `max()` with inline ternaries (`val if val > limit else limit`) or explicit `if/else` blocks inside heavily called helper functions to eliminate this overhead while preserving readability.
