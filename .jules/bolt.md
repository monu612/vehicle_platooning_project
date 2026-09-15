
## 2024-05-18 - Avoid standard library max()/min() in tight loops
**Learning:** Using Python's built-in `max()` and `min()` functions introduces significant function call overhead when executed hundreds of thousands of times inside tight loops (like edge evaluation during ACO path scoring). While `max()` and `min()` are Pythonic, in a performance-critical hot path, they become a bottleneck.
**Action:** Replace `max()` and `min()` with explicit `if/else` or `if/elif/else` conditional blocks in inner loops to bypass function call overhead. Always verify via benchmarking, and ensure readability is preserved by using multi-line blocks instead of deeply nested ternaries.
