## 2026-05-26 - Precomputing static NetworkX Topology Metrics
**Learning:** Re-computing generator methods like `nx.all_simple_paths` during inner simulation loops when the underlying base graph topology nodes remain identical is extremely inefficient in `networkx`, resulting in significant bottleneck overhead.
**Action:** When a graph is dynamically mutated (edges failing/recovering) but bounded by a base topology, pre-compute the bounded paths once for the static supergraph, and efficiently filter paths in the inner loop using `G._adj` for O(1) adjacency checks.
