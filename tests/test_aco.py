import random

import networkx as nx
import pytest

from aco import (
    select_path,
    update_pheromone,
    evaporate_all,
    deposit_elite,
    PHEROMONE_MIN,
    PHEROMONE_MAX,
)
from network import create_spider_web_topology


def test_select_path_returns_valid_route():
    graph = create_spider_web_topology(seed=123)

    path = select_path(graph, "M", "S6", alpha=1.0, beta=1.0, rng=random.Random(123))

    assert path is not None
    assert path[0] == "M"
    assert path[-1] == "S6"
    assert all(graph.has_edge(source, target) for source, target in zip(path, path[1:]))


def test_select_path_returns_none_for_missing_node():
    graph = create_spider_web_topology(seed=123)

    assert select_path(graph, "M", "UNKNOWN", alpha=1.0, beta=1.0) is None


def test_select_path_rejects_invalid_exploration_rate():
    graph = create_spider_web_topology(seed=123)

    with pytest.raises(ValueError):
        select_path(graph, "M", "S6", alpha=1.0, beta=1.0, exploration_rate=1.5)


def test_update_pheromone_increases_edges_on_valid_path():
    graph = create_spider_web_topology(seed=123)
    path = nx.shortest_path(graph, "M", "S6", weight="weight")
    before = [graph[source][target]["pheromone"] for source, target in zip(path, path[1:])]

    reward = update_pheromone(graph, path)
    after = [graph[source][target]["pheromone"] for source, target in zip(path, path[1:])]

    assert reward > 0
    assert all(new_value > old_value for old_value, new_value in zip(before, after))


def test_update_pheromone_ignores_invalid_path():
    graph = create_spider_web_topology(seed=123)

    assert update_pheromone(graph, ["M", "UNKNOWN"]) == 0.0


def test_update_pheromone_clamps_to_mmas_bounds():
    """Pheromone should never exceed PHEROMONE_MAX."""
    graph = create_spider_web_topology(seed=123)
    path = nx.shortest_path(graph, "M", "S6", weight="weight")

    # Deposit many times to push pheromone up.
    for _ in range(200):
        update_pheromone(graph, path, deposit_factor=50.0)

    for source, target in zip(path, path[1:]):
        assert graph[source][target]["pheromone"] <= PHEROMONE_MAX


def test_evaporate_all_reduces_pheromone():
    graph = create_spider_web_topology(seed=123)

    # Set pheromone high on all edges.
    for _, _, edge in graph.edges(data=True):
        edge["pheromone"] = 5.0

    evaporate_all(graph, rho=0.2)

    for _, _, edge in graph.edges(data=True):
        assert edge["pheromone"] < 5.0
        assert edge["pheromone"] >= PHEROMONE_MIN


def test_evaporate_all_respects_min_bound():
    graph = create_spider_web_topology(seed=123)

    # Evaporate many times — should never go below PHEROMONE_MIN.
    for _ in range(500):
        evaporate_all(graph, rho=0.5)

    for _, _, edge in graph.edges(data=True):
        assert edge["pheromone"] >= PHEROMONE_MIN


def test_evaporate_all_rejects_invalid_rho():
    graph = create_spider_web_topology(seed=123)

    with pytest.raises(ValueError):
        evaporate_all(graph, rho=1.5)


def test_deposit_elite_increases_pheromone_on_path():
    graph = create_spider_web_topology(seed=123)
    path = nx.shortest_path(graph, "M", "S6", weight="weight")
    before = [graph[s][t]["pheromone"] for s, t in zip(path, path[1:])]

    deposit_elite(graph, path, elite_factor=3.0)

    after = [graph[s][t]["pheromone"] for s, t in zip(path, path[1:])]
    assert all(a > b for a, b in zip(after, before))


def test_deposit_elite_ignores_empty_path():
    graph = create_spider_web_topology(seed=123)
    # Should not raise.
    deposit_elite(graph, None)
    deposit_elite(graph, [])
    deposit_elite(graph, ["M"])
def test_select_path_uses_precomputed_paths():
    graph = create_spider_web_topology(seed=123)

    precomputed = [["M", "S1", "S6"], ["M", "S6"]]

    # "M" -> "S6" shouldn't exist in our original topology, so it'll fail has_edge
    # Thus only "M" -> "S1" -> "S6" would remain in paths, but we must make sure the nodes exist and the edges exist
    # Let's add an edge M->S1 and S1->S6 if not exist, and remove M->S6 just in case
    if not graph.has_edge("M", "S1"):
        graph.add_edge("M", "S1")
    if not graph.has_edge("S1", "S6"):
        graph.add_edge("S1", "S6")
    if graph.has_edge("M", "S6"):
        graph.remove_edge("M", "S6")

    path = select_path(
        graph, "M", "S6", alpha=1.0, beta=1.0,
        exploration_rate=0.0,  # 0 to deterministically pick path
        rng=random.Random(123),
        precomputed_paths=precomputed
    )

    assert path == ["M", "S1", "S6"]
