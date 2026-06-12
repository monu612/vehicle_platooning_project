from __future__ import annotations

import argparse
import random

import matplotlib.pyplot as plt
import networkx as nx

from network import create_spider_web_topology
from aco import select_path, update_pheromone


def animate_realistic(steps: int = 40, seed: int | None = None) -> None:
    rng = random.Random(seed)
    G = create_spider_web_topology(rng=rng)
    nodes = list(G.nodes())

    pos = {node: [rng.uniform(0, 10), rng.uniform(0, 10)] for node in nodes}

    path_history = []

    all_simple_paths = {}
    for target in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        try:
            all_simple_paths[target] = list(nx.all_simple_paths(G, "M", target, cutoff=4))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            all_simple_paths[target] = []

    plt.ion()

    for i in range(steps):

        plt.clf()

        for node in pos:
            pos[node][0] += rng.uniform(-0.3, 0.3)
            pos[node][1] += rng.uniform(-0.3, 0.3)

        for u, v in G.edges():
            G[u][v]['weight'] *= rng.uniform(0.9, 1.1)
            G[u][v]['reliability'] *= rng.uniform(0.95, 1.05)
            G[u][v]['congestion'] *= rng.uniform(0.8, 1.2)

            G[u][v]['reliability'] = min(max(G[u][v]['reliability'], 0.5), 1.0)

        paths = []
        for target in ["S1", "S2", "S3", "S4", "S5", "S6"]:
            path = select_path(G, "M", target, rng=rng, precomputed_paths=all_simple_paths[target])
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
            edge_colors.append((1 - reliability, reliability, 0))

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate the vehicle platooning topology.")
    parser.add_argument("--steps", type=int, default=40, help="Number of animation frames.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    args = parser.parse_args()
    animate_realistic(steps=args.steps, seed=args.seed)


if __name__ == "__main__":
    main()
