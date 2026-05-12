import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
from network import create_spider_web_topology
from aco import select_path, update_pheromone

def animate_realistic(steps=40):

    G = create_spider_web_topology()
    nodes = list(G.nodes())

    # Smooth positions
    pos = {node: np.array([random.uniform(0, 10), random.uniform(0, 10)]) for node in nodes}

    # Store path history (for trail effect)
    path_history = []

    plt.ion()

    for i in range(steps):

        plt.clf()

        # 🔹 Smooth movement (vehicle motion)
        for node in pos:
            direction = np.random.uniform(-0.3, 0.3, size=2)
            pos[node] += direction

        # 🔹 Dynamic network conditions
        for u, v in G.edges():
            G[u][v]['weight'] *= random.uniform(0.9, 1.1)
            G[u][v]['reliability'] *= random.uniform(0.95, 1.05)
            G[u][v]['congestion'] *= random.uniform(0.8, 1.2)

            # Clamp reliability
            G[u][v]['reliability'] = min(max(G[u][v]['reliability'], 0.5), 1.0)

        # 🔹 Multi-vehicle routing (M → all)
        paths = []
        for target in ["S1", "S2", "S3", "S4", "S5", "S6"]:
            path = select_path(G, "M", target)
            if path:
                update_pheromone(G, path)
                paths.append(path)
                path_history.append(path)

        # -------------------------
        # DRAW EDGES (signal strength color)
        # -------------------------
        edge_colors = []
        for u, v in G.edges():
            reliability = G[u][v]['reliability']
            edge_colors.append((1 - reliability, reliability, 0))  # red → green

        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.5)

        # -------------------------
        # DRAW NODES
        # -------------------------
        node_colors = ['green' if n == "M" else 'skyblue' for n in nodes]

        nx.draw_networkx_nodes(G, pos,
                               node_color=node_colors,
                               node_size=900)

        nx.draw_networkx_labels(G, pos)

        # -------------------------
        # DRAW PATH TRAILS (faded)
        # -------------------------
        for old_path in path_history[-10:]:
            edges = [(old_path[j], old_path[j+1]) for j in range(len(old_path)-1)]
            nx.draw_networkx_edges(G, pos,
                                   edgelist=edges,
                                   edge_color='orange',
                                   width=1,
                                   alpha=0.2)

        # -------------------------
        # DRAW CURRENT PATHS (bold)
        # -------------------------
        for path in paths:
            edges = [(path[j], path[j+1]) for j in range(len(path)-1)]
            nx.draw_networkx_edges(G, pos,
                                   edgelist=edges,
                                   edge_color='red',
                                   width=3)

        # -------------------------
        # TITLE + INFO
        # -------------------------
        plt.title(f"Real-Time Vehicle Communication (Step {i+1})")

        plt.pause(0.4)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    animate_realistic()