## 2026-10-21 - CI Pipeline Strictness
**Learning:** The GitHub CI pipeline is extremely strict, and will fail if any `flake8` errors from `--select=E9,F63,F7,F82` are present, even if they aren't part of the changes made. Additionally, it requires an `environment.yml` for conda.
**Action:** When working on performance optimizations, ensure that any existing critical linting errors blocking the CI are resolved and dependencies are correctly configured, even if they seem out-of-scope for the primary task.
