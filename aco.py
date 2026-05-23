import random
import networkx as nx

def select_path(G, source, target, alpha=2, beta=3, exploration_rate=0.3, precomputed_paths=None):

    if precomputed_paths is not None:
        # Filter precomputed paths to only those where all edges still exist in the current graph
        paths = [
            path for path in precomputed_paths
            if all(G.has_edge(path[i], path[i+1]) for i in range(len(path) - 1))
        ]
    else:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=4))

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