## 2026-10-02 - Micro-optimizing edge metrics inside hot loops
**Learning:** Python's built-in `min()` and `max()` functions add significant function call overhead when used repeatedly inside extremely tight loops like evaluating edges in path scoring during ACO pathfinding.
**Action:** Replace `min()` and `max()` with simple inline ternary operations (e.g., `value if value > min_value else min_value`) or `if/else` blocks inside frequently called helper functions to reduce overhead without sacrificing readability for callers.
