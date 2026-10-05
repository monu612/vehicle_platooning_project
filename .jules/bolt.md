## 2024-05-18 - Replacing min/max overhead
**Learning:** Codebase-specific performance pattern: Replacing Python's built-in min() and max() functions with inline ternary operations (e.g., val if val > min_val else min_val) or if/else blocks inside extremely tight loops reduces function call overhead.
**Action:** Break nested ternaries into simple if/else blocks for min/max logic in helper functions (like _edge_metric and _clamp_pheromone) to achieve performance gains without cluttering the caller's scope.
