## 2024-05-24 - Avoiding min/max overhead in Python

**Learning:** Python's built-in min() and max() functions can introduce measurable overhead when called extremely frequently in tight loops (e.g., scoring hundreds of thousands of edges during pathfinding).

**Action:** Replace min()/max() calls inside frequently-called small helper functions with simple if/else blocks or ternary operators to achieve performance gains without cluttering the caller's scope.
