## 2024-10-31 - Precompute Static Paths to eliminate all_simple_paths overhead
**Learning:** For pathfinding on dynamic networkx graphs, caching generator-based algorithms like `nx.all_simple_paths` on a pristine static base topology *before* the simulation loop begins, and dynamically filtering them inside the loop, significantly speeds up performance compared to dynamically recalculating simple paths per iteration.
**Action:** When working with dynamic networkx simulations where edges change, identify if path generation can be precomputed on a static base state and filtered later rather than executing the pathfinding algorithm per step.

## 2024-10-31 - Avoiding hardcoded literals in optimizations
**Learning:** When adding constants to default function signatures in generic algorithms (like `cutoff=4`), defining a single constant (e.g. `MAX_PATH_CUTOFF`) and reusing it ensures that caller precomputations stay synchronized with defaults, avoiding potential inconsistencies if defaults are later updated.
**Action:** When creating new precomputation behaviors that duplicate a magic number parameter, extract the number to a named constant and use it in both the calling site and the signature.
