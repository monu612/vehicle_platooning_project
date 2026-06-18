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


def _add_edge(G: nx.Graph, u: str, v: str, rng: random.Random) -> None:
    """Add one edge with randomised simulation attributes."""
    G.add_edge(
        u, v,
        weight=rng.uniform(1.0, 10.0),         # latency
        pheromone=1.0,
        reliability=rng.uniform(0.7, 1.0),
        congestion=rng.uniform(0.5, 1.5),
    )


def create_spider_web_topology(
    seed: int | None = None,
    rng: random.Random | None = None,
) -> nx.Graph:
    """Create the original 7-node vehicle communication topology."""
    rng = _build_rng(seed, rng)
    G: nx.Graph = nx.Graph()

    G.add_nodes_from(NODES)

    for u, v in EDGES:
        _add_edge(G, u, v, rng)

    return G


def create_platoon(
    n_vehicles: int = 7,
    seed: int | None = None,
    rng: random.Random | None = None,
) -> nx.Graph:
    """Create a scalable platoon topology with *n_vehicles* nodes.

    The topology is a chain of vehicles with extra lateral links to form a
    mesh-like structure.  Node 0 is the master ("M"), the rest are followers
    ("S1", "S2", ...).

    For the default ``n_vehicles=7`` the result is identical in shape to
    :func:`create_spider_web_topology`.
    """
    if n_vehicles < 2:
        raise ValueError("A platoon needs at least 2 vehicles.")

    rng = _build_rng(seed, rng)
    G: nx.Graph = nx.Graph()

    nodes = ["M"] + [f"S{i}" for i in range(1, n_vehicles)]
    G.add_nodes_from(nodes)

    # Chain links: M -> S1 -> S2 -> ... -> S(n-1)
    for i in range(len(nodes) - 1):
        _add_edge(G, nodes[i], nodes[i + 1], rng)

    # Skip links: connect every other vehicle for redundancy
    for i in range(len(nodes) - 2):
        _add_edge(G, nodes[i], nodes[i + 2], rng)

    # A few extra random lateral links for larger platoons
    for i in range(len(nodes) - 3):
        if rng.random() < 0.4:
            _add_edge(G, nodes[i], nodes[i + 3], rng)

    return G
