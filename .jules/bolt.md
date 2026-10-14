## 2026-10-14 - Optimize dictionary wrappers
**Learning:** Inlining generic wrapper functions (like dictionary `.get()` lookups) extensively in tight loops can lead to unreadable boilerplate. However, replacing `max()`/`min()` with ternary operators inside the helper itself achieves performance gains without cluttering the caller's scope.
**Action:** Use simple if/else or ternary blocks instead of built-in min/max functions inside tight loop helpers to reduce function call overhead.
