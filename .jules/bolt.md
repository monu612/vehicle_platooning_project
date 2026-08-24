## 2024-05-24 - Avoiding zip in tight path iteration loops
**Learning:** For tight inner loops iterating over consecutive elements in a sequence, replacing `zip(path, path[1:])` with an index-based loop using `range(len(path) - 1)` significantly reduces execution overhead by completely avoiding the memory allocation from list slicing and the tuple packing inherent to `zip`.
**Action:** Always prefer index-based iteration over `zip` with slicing when traversing paths in performance-critical sections like path evaluation or latency calculation.
