from __future__ import annotations

import math
import random
from collections.abc import Sequence

import networkx as nx


MIN_EDGE_COST = 1e-9


def _path_score(
    G: nx.Graph,
    path: Sequence[str],
    alpha: float,
    beta: float,
) -> float:
    pheromone = 1.0
    heuristic = 1.0

    for source, target in zip(path, path[1:]):
        edge = G[source][target]

        # Optimization: Inline metric access and bound checks to avoid function
        # call and max() overhead in this hot loop.
        latency = float(edge.get("weight", 1.0))
        if latency <= MIN_EDGE_COST:
            latency = MIN_EDGE_COST

        congestion = float(edge.get("congestion", 1.0))
        if congestion <= MIN_EDGE_COST:
            congestion = MIN_EDGE_COST

        reliability = float(edge.get("reliability", 1.0))
        if reliability <= MIN_EDGE_COST:
            reliability = MIN_EDGE_COST
        elif reliability > 1.0:
            reliability = 1.0

        edge_pheromone = float(edge.get("pheromone", 1.0))
        if edge_pheromone <= MIN_EDGE_COST:
            edge_pheromone = MIN_EDGE_COST

        effective_cost = latency * congestion
        heuristic *= (reliability / effective_cost) ** beta
        pheromone *= edge_pheromone ** alpha

    score = pheromone * heuristic
    return score if math.isfinite(score) and score > 0 else 0.0


def select_path(
    G: nx.Graph,
    source: str,
    target: str,
    alpha: float = 2.0,
    beta: float = 3.0,
    exploration_rate: float = 0.3,
    cutoff: int = 4,
    rng: random.Random | None = None,
) -> list[str] | None:
    """Select a route using ant-colony pheromone and edge quality metrics."""
    if not 0.0 <= exploration_rate <= 1.0:
        raise ValueError("exploration_rate must be between 0 and 1.")

    rng = rng or random.Random()

    try:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=cutoff))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

    if not paths:
        return None

    if rng.random() < exploration_rate:
        return rng.choice(paths)

    scores = [_path_score(G, path, alpha, beta) for path in paths]

    total = sum(scores)

    if total <= 0:
        return rng.choice(paths)

    probabilities = [s / total for s in scores]

    return rng.choices(paths, weights=probabilities, k=1)[0]


def update_pheromone(
    G: nx.Graph,
    path: Sequence[str] | None,
    rho: float = 0.1,
    deposit_factor: float = 5.0,
) -> float:
    """Update pheromone on a path and return the deposited reward."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be between 0 and 1.")

    if not path or len(path) < 2:
        return 0.0

    edges = []
    total_latency = 0.0

    for source, target in zip(path, path[1:]):
        if not G.has_edge(source, target):
            return 0.0

        edges.append((source, target))

        # Optimization: Inline metric lookup and bounds check
        weight = float(G[source][target].get("weight", 1.0))
        if weight <= MIN_EDGE_COST:
            weight = MIN_EDGE_COST
        total_latency += weight

    reward = deposit_factor / total_latency

    for source, target in edges:
        edge = G[source][target]

        # Optimization: Inline metric lookup and bounds check
        current = float(edge.get("pheromone", 1.0))
        if current <= MIN_EDGE_COST:
            current = MIN_EDGE_COST

        edge["pheromone"] = (1 - rho) * current + reward

    return reward
