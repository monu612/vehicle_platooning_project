from __future__ import annotations

import random

import networkx as nx


NODES = ("M", "S1", "S2", "S3", "S4", "S5", "S6")

EDGES = (
    ("M", "S1"), ("M", "S2"), ("M", "S3"),
    ("S1", "S2"), ("S2", "S3"),
    ("S1", "S4"), ("S2", "S5"), ("S3", "S6"),
    ("S4", "S5"), ("S5", "S6"),
    ("S2", "S6"), ("S3", "S5"),
)


def _build_rng(seed: int | None, rng: random.Random | None) -> random.Random:
    if seed is not None and rng is not None:
        raise ValueError("Pass either seed or rng, not both.")

    return rng if rng is not None else random.Random(seed)


def create_spider_web_topology(
    seed: int | None = None,
    rng: random.Random | None = None,
) -> nx.Graph:
    """Create the vehicle communication topology used by the simulation."""
    rng = _build_rng(seed, rng)
    G: nx.Graph = nx.Graph()

    G.add_nodes_from(NODES)

    for u, v in EDGES:
        G.add_edge(
            u, v,
            weight=rng.uniform(1.0, 10.0),         # latency
            pheromone=1.0,
            reliability=rng.uniform(0.7, 1.0),
            congestion=rng.uniform(0.5, 1.5),
        )

    return G
