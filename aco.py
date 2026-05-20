import random
import networkx as nx

_paths_cache = {}
MAX_CACHE_SIZE = 1024

def select_path(G, source, target, alpha=2, beta=3, exploration_rate=0.3):
    """
    Selects a path using Ant Colony Optimization.
    Optimized: Caches all_simple_paths based on the graph's available edges to avoid
    expensive redundant calculations during simulations with link failures.
    """
    edge_key = frozenset(G.edges())
    cache_key = (source, target, edge_key)

    if cache_key not in _paths_cache:
        if len(_paths_cache) >= MAX_CACHE_SIZE:
            _paths_cache.clear()
        # Cache as tuple to prevent accidental modification by downstream code
        _paths_cache[cache_key] = tuple(nx.all_simple_paths(G, source, target, cutoff=4))

    paths = _paths_cache[cache_key]

    if not paths:
        return None

    # Exploration
    if random.random() < exploration_rate:
        return random.choice(paths)

    # Exploitation
    scores = []

    for path in paths:
        pheromone = 1.0
        heuristic = 1.0

        for i in range(len(path) - 1):
            edge = G[path[i]][path[i+1]]

            effective_cost = edge['weight'] * edge['congestion']

            heuristic *= (edge['reliability'] / effective_cost) ** beta
            pheromone *= edge['pheromone'] ** alpha

        scores.append(pheromone * heuristic)

    total = sum(scores)

    if total == 0:
        return random.choice(paths)

    probabilities = [s / total for s in scores]

    return random.choices(paths, weights=probabilities)[0]


def update_pheromone(G, path, rho=0.1):

    if not path:
        return

    total_latency = 0

    for i in range(len(path) - 1):
        total_latency += G[path[i]][path[i+1]]['weight']

    reward = 5 / total_latency

    for i in range(len(path) - 1):
        edge = G[path[i]][path[i+1]]

        edge['pheromone'] = (
            (1 - rho) * edge['pheromone'] + reward
        )