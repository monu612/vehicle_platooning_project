## 2026-08-22 - Python Function Call Overhead in Tight Loops
**Learning:** Function call overhead inside tightly nested loops (like scoring paths in ACO) can significantly bottleneck Python performance.
**Action:** When optimizing tight inner loops in Python, consider manually inlining generic utility functions or accessors to avoid the overhead of function invocation and tuple packing.
