## 2026-08-25 - Inlining wrappers in hot loops
**Learning:** In Python, calling generic wrapper functions (like `_edge_metric` which does a dict lookup and a min/max clamp) inside tight loops (like path scoring over all simple paths) incurs significant function call overhead, dominating execution time.
**Action:** For tight inner loops, inline simple wrappers directly and avoid extra function calls.

## 2026-08-25 - Avoid `zip` in hot consecutive-element iteration
**Learning:** For tight inner loops iterating over consecutive elements in a sequence, replacing `zip(path, path[1:])` with an index-based loop using `range(len(path) - 1)` significantly reduces execution overhead by completely avoiding the memory allocation from list slicing and the tuple packing inherent to `zip`.
**Action:** Use index-based loops instead of `zip` with slicing when traversing path segments in performance-critical code.

## 2026-08-25 - Satisfying Conda CI Requirements
**Learning:** The project's GitHub Actions CI pipeline uses Conda to setup the environment. If it errors out because `environment.yml` is missing, we must satisfy the CI constraint by creating an `environment.yml` that defines the `base` environment and includes dependencies matching `pyproject.toml`.
**Action:** Do not alter CI workflow files to bypass a build error; instead, provide the missing configuration file expected by the pipeline.
