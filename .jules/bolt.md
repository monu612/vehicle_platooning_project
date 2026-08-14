## 2026-08-14 - Precomputing Static Paths in Dynamic Graphs
**Learning:** In dynamically changing networkx graphs (like link failure simulations), dynamically computing `nx.all_simple_paths` on every iteration is extremely slow. We can precompute simple paths on the pristine static topology before mutations occur, and pass them into the iteration loop. We can then filter the precomputed paths dynamically per iteration by quickly verifying if every consecutive edge exists using `G.has_edge(u, v)`.
**Action:** Identify expensive pathfinding functions called in iteration loops and check if they can be cached on a static base topology and filtered cheaply during dynamically disrupted states.

## 2026-08-14 - Inlining Generic Accessors
**Learning:** Using a generic wrapper function like `_edge_metric` that reads from a dictionary with a fallback value (e.g. `edge.get("name", default)`) adds considerable function call overhead when executed tightly in a hot path like `_path_score`.
**Action:** When a loop is executed heavily, inline simple getter logic directly to bypass the function call overhead.
