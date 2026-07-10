## 2026-07-10 - [ACO Pathfinding Latency Bottleneck]
**Learning:** During profiling, `select_path` was found to spend most of its time in `nx.all_simple_paths`. NetworkX's `all_simple_paths` generates paths at runtime based on the dynamic graph state, which is computationally expensive during simulation loop iterations where edges mutate frequently.
**Action:** Pre-compute simple paths on the pristine static topology before mutations occur, and dynamically filter them using `G.has_edge()` to avoid recreating paths in every loop iteration while preserving robustness against temporary edge removals.
## 2026-07-10 - [Missing Arguments in `select_path` Calls]
**Learning:** Some test cases calling `select_path` (e.g. in `tests/test_aco.py`) and scripts like `visualization.py` fail because they are missing required positional arguments (`alpha`, `beta`). These issues are pre-existing in the codebase but cause CI failures.
**Action:** When working on `select_path`, explicitly verify if tests run correctly. Since these are pre-existing test failures outside the scope of our performance optimization, we'll fix them to make CI pass, passing `alpha=1.0` and `beta=1.0` as required arguments.
