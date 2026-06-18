import pytest
import networkx as nx

from network import EDGES, NODES, create_spider_web_topology, create_platoon


def test_create_spider_web_topology_has_expected_nodes_and_edges():
    graph = create_spider_web_topology(seed=123)

    assert set(graph.nodes) == set(NODES)
    assert graph.number_of_edges() == len(EDGES)
    assert nx.is_connected(graph)


def test_edges_have_required_simulation_attributes():
    graph = create_spider_web_topology(seed=123)

    for _, _, edge in graph.edges(data=True):
        assert 1.0 <= edge["weight"] <= 10.0
        assert edge["pheromone"] == 1.0
        assert 0.7 <= edge["reliability"] <= 1.0
        assert 0.5 <= edge["congestion"] <= 1.5


def test_seed_makes_topology_repeatable():
    graph_a = create_spider_web_topology(seed=99)
    graph_b = create_spider_web_topology(seed=99)

    assert sorted(graph_a.edges(data=True)) == sorted(graph_b.edges(data=True))


# --- create_platoon tests ---

def test_create_platoon_default_size():
    graph = create_platoon(seed=42)

    assert "M" in graph.nodes
    assert graph.number_of_nodes() == 7
    assert nx.is_connected(graph)


def test_create_platoon_various_sizes():
    for n in (2, 5, 10, 15):
        graph = create_platoon(n_vehicles=n, seed=42)
        assert graph.number_of_nodes() == n
        assert nx.is_connected(graph)


def test_create_platoon_too_small():
    with pytest.raises(ValueError, match="at least 2"):
        create_platoon(n_vehicles=1)


def test_create_platoon_edges_have_attributes():
    graph = create_platoon(n_vehicles=10, seed=42)

    for _, _, edge in graph.edges(data=True):
        assert "weight" in edge
        assert "pheromone" in edge
        assert "reliability" in edge
        assert "congestion" in edge
