import networkx as nx
import random

def create_spider_web_topology():
    G = nx.Graph()

    # Add vehicles (1 master + 6 slaves)
    nodes = ["M", "S1", "S2", "S3", "S4", "S5", "S6"]
    G.add_nodes_from(nodes)

    # Spider-web connections (multi-hop + redundancy)
    edges = [
        ("M", "S1"), ("M", "S2"), ("M", "S3"),
        ("S1", "S2"), ("S2", "S3"),
        ("S1", "S4"), ("S2", "S5"), ("S3", "S6"),
        ("S4", "S5"), ("S5", "S6"),
        ("S4", "S2"), ("S5", "S3")
    ]

    # Assign latency + pheromone
    for u, v in edges:
        G.add_edge(
            u, v,
            weight=random.uniform(1, 10),   # latency
            pheromone=1.0                   # initial pheromone
        )

    return G