## 2024-05-24 - min() and max() function call overhead in tight loops
**Learning:** Replacing Python's built-in min() and max() functions with inline ternary operations or if/else blocks inside extremely tight loops significantly reduces function call overhead.
**Action:** Use inline ternary operations (e.g., val if val > min_val else min_val) or if/else blocks instead of min/max in high-frequency hot paths to achieve performance gains without cluttering the caller's scope.
