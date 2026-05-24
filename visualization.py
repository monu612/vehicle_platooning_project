from __future__ import annotations

import argparse
import random

import matplotlib.pyplot as plt
import networkx as nx

from network import create_spider_web_topology
from aco import select_path, update_pheromone


def animate_network(steps: int = 25, pause_time: float = 0.8, seed: int | None = None) -> None:
    rng = random.Random(seed)
    G = create_spider_web_topology(rng=rng)

    pos = nx.spring_layout(G, seed=42)

    plt.ion()

    for i in range(steps):

        plt.clf()

        for u, v in G.edges():
            G[u][v]['weight'] *= rng.uniform(0.9, 1.1)

        exploration_rate = max(0.05, 0.3 * (1 - i / steps))
        path = select_path(G, "M", "S6", exploration_rate=exploration_rate, rng=rng)

        if path:
            update_pheromone(G, path)

        # -------------------------
        # NODE COLORS
        # -------------------------
        node_colors = []
        for node in G.nodes():
            if node == "M":
                node_colors.append("green")   # Master node
            else:
                node_colors.append("skyblue")

        # -------------------------
        # DRAW GRAPH
        # -------------------------
        nx.draw(
            G, pos,
            with_labels=True,
            node_color=node_colors,
            node_size=900,
            font_size=10,
            edge_color='gray'
        )

        # -------------------------
        # HIGHLIGHT SELECTED PATH
        # -------------------------
        if path:
            path_edges = [(path[j], path[j+1]) for j in range(len(path)-1)]

            nx.draw_networkx_edges(
                G, pos,
                edgelist=path_edges,
                edge_color='red',
                width=3
            )

        # -------------------------
        # EDGE LABELS (Latency)
        # -------------------------
        edge_labels = {
            (u, v): f"{G[u][v]['weight']:.1f}"
            for u, v in G.edges()
        }

        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_size=7
        )

        # -------------------------
        # TITLE
        # -------------------------
        plt.title(f"ACO-Based Vehicle Communication (Step {i+1})")

        plt.pause(pause_time)

    plt.ioff()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate a single ACO route.")
    parser.add_argument("--steps", type=int, default=25, help="Number of animation frames.")
    parser.add_argument("--pause-time", type=float, default=0.8, help="Pause between frames in seconds.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    args = parser.parse_args()
    animate_network(steps=args.steps, pause_time=args.pause_time, seed=args.seed)


if __name__ == "__main__":
    main()
