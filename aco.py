from __future__ import annotations

import math
import random
import functools
from collections.abc import Sequence
from typing import Any

import networkx as nx

MIN_EDGE_COST = 1e-9

# MMAS bounds — prevents stagnation and premature convergence.
PHEROMONE_MIN = 0.1
PHEROMONE_MAX = 10.0


def _edge_metric(edge: dict, name: str, default: float) -> float:
    value = float(edge.get(name, default))
    return max(value, MIN_EDGE_COST)


def _clamp_pheromone(value: float) -> float:
    """Clamp pheromone to MMAS bounds."""
    return max(PHEROMONE_MIN, min(value, PHEROMONE_MAX))


def get_network_state(G: nx.Graph) -> tuple[float, float, float]:
    """Calculate average congestion, average reliability, and network instability."""
    if not G.edges:
        return 1.0, 1.0, 0.0

    total_congestion = 0.0
    total_reliability = 0.0
    count = 0

    for _, _, data in G.edges(data=True):
        total_congestion += data.get("congestion", 1.0)
        total_reliability += data.get("reliability", 1.0)
        count += 1

    avg_congestion = total_congestion / count
    avg_reliability = total_reliability / count

    # Instability = 1 - (AvgReliability / AvgCongestion)
    instability = 1.0 - (avg_reliability / avg_congestion) if avg_congestion > 0 else 0.0

    return avg_congestion, avg_reliability, max(0.0, instability)


def adaptive_parameters(
    avg_congestion: float,
    avg_reliability: float,
    failure_rate: float,
) -> tuple[float, float, float]:
    """Compute dynamic ACO parameters based on network conditions."""
    alpha_0 = 2.0
    beta_0 = 1.0
    rho_0 = 0.05

    # k values tuned for requested AS-ACO behavior
    k1 = 5.0
    k2 = 1.0
    k3 = 0.5

    instability = max(0.0, 1.0 - (avg_reliability / avg_congestion)) if avg_congestion > 0 else 0.0

    alpha_t = alpha_0 + k1 * failure_rate
    beta_t = beta_0 + k2 * avg_congestion
    rho_t = rho_0 + k3 * instability

    return alpha_t, beta_t, min(0.99, max(0.01, rho_t))


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


# Pre-compute simple paths using an LRU cache to prevent memory leaks
# with changing topologies.
@functools.lru_cache(maxsize=128)
def _get_simple_paths(
    edges: tuple[tuple[str, str], ...],
    source: str,
    target: str,
    cutoff: int,
    is_directed: bool
) -> list[tuple[str, ...]]:
    """Cached helper to fetch all simple paths for a given static topology."""
    # Reconstruct a basic graph just for pathfinding based on the edge set.
    G: Any = nx.DiGraph() if is_directed else nx.Graph()
    G.add_edges_from(edges)

    paths = nx.all_simple_paths(G, source, target, cutoff=cutoff)
    return [tuple(p) for p in paths]


def select_path(
    G: nx.Graph,
    source: str,
    target: str,
    alpha: float,
    beta: float,
    exploration_rate: float = 0.3,
    cutoff: int = 4,
    rng: random.Random | None = None,
) -> list[str] | None:
    """Select a route using ant-colony pheromone and edge quality metrics."""
    if not 0.0 <= exploration_rate <= 1.0:
        raise ValueError("exploration_rate must be between 0 and 1.")

    rng = rng or random.Random()

    try:
        # Optimization: Cache all_simple_paths based on the current edges.
        # nx.all_simple_paths is extremely slow when called repeatedly.
        # Use a sorted tuple of edges to handle the graph state reliably.
        if G.is_directed():
            edges = tuple(sorted(G.edges()))
        else:
            edge_gen = ((u, v) if u <= v else (v, u) for u, v in G.edges())
            edges = tuple(sorted(edge_gen))

        paths_tuple = _get_simple_paths(
            edges, source, target, cutoff, G.is_directed()
        )

        # Convert tuples back to lists since caller expects list[str]
        paths = [list(p) for p in paths_tuple]
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
    """Update pheromone on a successful path and return deposited reward."""
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
        edge["pheromone"] = _clamp_pheromone((1 - rho) * current + reward)

    return reward


def evaporate_all(G: nx.Graph, rho: float = 0.1) -> None:
    """Apply global pheromone evaporation to every edge in the graph.

    This must be called once per iteration *before* path selection to prevent
    unbounded pheromone accumulation.
    """
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be between 0 and 1.")

    for _, _, edge in G.edges(data=True):
        current = edge.get("pheromone", 1.0)
        edge["pheromone"] = _clamp_pheromone((1 - rho) * current)


def deposit_elite(
    G: nx.Graph,
    best_path: Sequence[str] | None,
    elite_factor: float = 2.0,
) -> None:
    """Give the global-best path a bonus pheromone deposit."""
    if not best_path or len(best_path) < 2:
        return

    total_latency = 0.0
    edges = []
    for source, target in zip(best_path, best_path[1:]):
        if not G.has_edge(source, target):
            return
        edges.append((source, target))
        total_latency += _edge_metric(G[source][target], "weight", 1.0)

    bonus = elite_factor / total_latency

    for source, target in edges:
        edge = G[source][target]
        edge["pheromone"] = _clamp_pheromone(edge.get("pheromone", 1.0) + bonus)
