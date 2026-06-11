from __future__ import annotations

import math
import random
from collections.abc import Sequence

import networkx as nx


MIN_EDGE_COST = 1e-9


def _edge_metric(edge: dict, name: str, default: float) -> float:
    value = float(edge.get(name, default))
    return max(value, MIN_EDGE_COST)


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
        latency = _edge_metric(edge, "weight", 1.0)
        congestion = _edge_metric(edge, "congestion", 1.0)
        reliability = min(_edge_metric(edge, "reliability", 1.0), 1.0)
        edge_pheromone = _edge_metric(edge, "pheromone", 1.0)

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
    precomputed_paths: Sequence[Sequence[str]] | None = None,
) -> list[str] | None:
    """Select a route using ant-colony pheromone and edge quality metrics."""
    if not 0.0 <= exploration_rate <= 1.0:
        raise ValueError("exploration_rate must be between 0 and 1.")

    rng = rng or random.Random()

    if precomputed_paths is not None:
        # Optimization: filter precomputed paths for edge failures on dynamic topology.
        # This is ~8x faster than recomputing nx.all_simple_paths per tick.
        paths = []
        for p in precomputed_paths:
            valid = True
            for u, v in zip(p, p[1:]):
                if not G.has_edge(u, v):
                    valid = False
                    break
            if valid:
                paths.append(list(p))
    else:
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
    """Update pheromone on a successful path and return the deposited reward."""
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
        total_latency += _edge_metric(G[source][target], "weight", 1.0)

    reward = deposit_factor / total_latency

    for source, target in edges:
        edge = G[source][target]
        current = _edge_metric(edge, "pheromone", 1.0)
        edge["pheromone"] = (1 - rho) * current + reward

    return reward
