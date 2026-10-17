## 2024-10-18 - Replacing min/max with if/else in Python tight loops
**Learning:** Python's built-in min/max functions have significant function call overhead compared to simple if/else blocks when used in extremely tight loops (like edge metric extraction during graph traversals).
**Action:** When micro-optimizing critical algorithmic paths, replace min/max bounds checking with direct if/else logic for measurable performance gains without sacrificing readability.
