## 2024-05-17 - Readme and Project Context
**Learning:** Understanding the project structure and context is key.
**Action:** Always start by reading the README and key files.

## 2024-05-17 - Precomputing Paths for Dynamic Graphs
**Learning:** Calling nx.all_simple_paths inside a hot loop (like a simulation iteration over a mutated graph) is a significant performance bottleneck.
**Action:** Precompute simple paths on the pristine static base topology *before* any dynamic mutations occur, and filter them dynamically in each iteration by verifying if every consecutive edge still exists.
