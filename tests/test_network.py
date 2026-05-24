import networkx as nx

from network import EDGES, NODES, create_spider_web_topology


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
