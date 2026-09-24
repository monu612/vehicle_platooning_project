## 2024-09-24 - Avoid min()/max() built-ins in tight inner loops
**Learning:** Python's built-in `min()` and `max()` functions incur noticeable function call overhead when executed repeatedly in extremely tight inner loops (like edge scoring or pheromone clamping in ACO).
**Action:** Replace `min()` and `max()` with simple `if/else` control flow blocks inside these helper functions to significantly reduce microsecond overhead without impacting the caller's code readability.
