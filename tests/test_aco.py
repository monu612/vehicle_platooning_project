import random

import networkx as nx
import pytest

from aco import select_path, update_pheromone
from network import create_spider_web_topology


def test_select_path_returns_valid_route():
    graph = create_spider_web_topology(seed=123)

    path = select_path(graph, "M", "S6", rng=random.Random(123))

    assert path is not None
    assert path[0] == "M"
    assert path[-1] == "S6"
    assert all(
        graph.has_edge(source, target)
        for source, target in zip(path, path[1:])
    )


def test_select_path_returns_none_for_missing_node():
    graph = create_spider_web_topology(seed=123)

    assert select_path(graph, "M", "UNKNOWN") is None


def test_select_path_rejects_invalid_exploration_rate():
    graph = create_spider_web_topology(seed=123)

    with pytest.raises(ValueError):
        select_path(graph, "M", "S6", exploration_rate=1.5)


def test_update_pheromone_increases_edges_on_valid_path():
    graph = create_spider_web_topology(seed=123)
    path = nx.shortest_path(graph, "M", "S6", weight="weight")
    before = [
        graph[source][target]["pheromone"]
        for source, target in zip(path, path[1:])
    ]

    reward = update_pheromone(graph, path)
    after = [
        graph[source][target]["pheromone"]
        for source, target in zip(path, path[1:])
    ]

    assert reward > 0
    assert all(
        new_value > old_value
        for old_value, new_value in zip(before, after)
    )


def test_update_pheromone_ignores_invalid_path():
    graph = create_spider_web_topology(seed=123)

    assert update_pheromone(graph, ["M", "UNKNOWN"]) == 0.0
