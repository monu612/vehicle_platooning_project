## 2024-05-24 - Dynamic NetworkX Graph Pathfinding Pattern
**Learning:** `nx.all_simple_paths` is computationally expensive to call continuously inside a simulation loop on a dynamically mutating graph, especially since our network nodes are static and only edges change.
**Action:** Always precompute simple paths upfront on the pristine static topology and filter them within the simulation loop using `all(G.has_edge(u,v))` for an O(P*E) check per path rather than re-traversing the graph. Avoid lazy initialization during disrupted state, as it omits temporarily broken paths permanently.
