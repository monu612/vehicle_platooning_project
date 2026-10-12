## 2024-05-24 - Function call overhead in tight loops
**Learning:** Python's built-in min() and max() functions have significant call overhead when used on scalar values inside extremely tight loops (like _edge_metric).
**Action:** Replace min() and max() with simple if/else blocks in hot paths to achieve significant performance gains without sacrificing readability.
