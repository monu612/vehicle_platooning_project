## 2026-08-31 - [Optimization: Avoid zip in tight loops]
**Learning:** In tight inner loops iterating over consecutive elements in a sequence, replacing `zip(path, path[1:])` with an index-based loop using `range(len(path) - 1)` significantly reduces execution overhead by completely avoiding the memory allocation from list slicing and the tuple packing inherent to `zip`. Also, inlining dictionary lookups avoids overhead.
**Action:** Update `aco.py` and `simulation.py` to use indexed loops for path iteration, and inline dictionary lookups.
