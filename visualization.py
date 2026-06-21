from __future__ import annotations

import argparse
import random

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from matplotlib.animation import FuncAnimation

from network import create_spider_web_topology
from aco import select_path, update_pheromone, evaporate_all


# --- Dark palette ---
BG_COLOR = "#0f0f0f"
CARD_BG = "#1e1e2e"
MASTER_COLOR = "#00ff88"
NODE_COLOR = "#00d4ff"
PATH_COLOR = "#ff5577"
GRID_COLOR = "#333355"
TEXT_COLOR = "#ffffff"
PHEROMONE_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "pheromone_viz", ["#1e1e2e", "#00d4ff", "#00ff88"]
)


def animate_network(
    steps: int = 30,
    pause_time: float = 0.5,
    seed: int | None = None,
    target_node: str = "S6",
    save_gif: bool = False,
    output_path: str = "output/single_route_animation.gif",
) -> None:
    """Animate a single ACO route from M → target_node."""
    rng = random.Random(seed)
    G = create_spider_web_topology(rng=rng)

    pos = nx.spring_layout(G, seed=42, k=2.0)

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(BG_COLOR)

    latency_history: list[float] = []

    # Pre-compute simple paths
    try:
        aco_paths = list(nx.all_simple_paths(G, "M", target_node, cutoff=4))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        aco_paths = []

    def update(frame: int):
        ax.clear()
        ax.set_facecolor(BG_COLOR)
        ax.axis("off")

        # --- Perturb edges ---
        evaporate_all(G, rho=0.05)
        for u, v in G.edges():
            G[u][v]["weight"] = max(0.5, G[u][v]["weight"] * rng.uniform(0.92, 1.08))

        exploration_rate = max(0.05, 0.3 * (1 - frame / steps))
        path = select_path(G, "M", target_node, alpha=2.0, beta=1.0, exploration_rate=exploration_rate, rng=rng, precomputed_paths=aco_paths)

        if path:
            update_pheromone(G, path)
            lat = sum(G[path[j]][path[j + 1]].get("weight", 1.0) for j in range(len(path) - 1))
            latency_history.append(lat)

        # --- Draw edges with pheromone coloring ---
        pheromone_vals = [G[u][v].get("pheromone", 1.0) for u, v in G.edges()]
        p_min = min(pheromone_vals) if pheromone_vals else 0.1
        p_max = max(pheromone_vals) if pheromone_vals else 10.0
        if p_max == p_min:
            p_max = p_min + 1

        for u, v in G.edges():
            p = G[u][v].get("pheromone", 1.0)
            norm = (p - p_min) / (p_max - p_min)
            color = PHEROMONE_CMAP(norm)
            width = 1.0 + norm * 3.0
            ax.plot(
                [pos[u][0], pos[v][0]],
                [pos[u][1], pos[v][1]],
                color=color, linewidth=width, alpha=0.5, zorder=1,
            )

        # --- Edge labels (latency) ---
        for u, v in G.edges():
            mx = (pos[u][0] + pos[v][0]) / 2
            my = (pos[u][1] + pos[v][1]) / 2
            ax.text(mx, my, f"{G[u][v]['weight']:.1f}", fontsize=6.5,
                    color="#888888", ha="center", va="center", zorder=2)

        # --- Highlight current path ---
        if path:
            for j in range(len(path) - 1):
                u, v = path[j], path[j + 1]
                ax.plot(
                    [pos[u][0], pos[v][0]],
                    [pos[u][1], pos[v][1]],
                    color=PATH_COLOR, linewidth=3.5, alpha=0.9, zorder=4,
                )

        # --- Draw nodes ---
        for node in G.nodes():
            x, y = pos[node]
            is_master = node == "M"
            is_target = node == target_node
            color = MASTER_COLOR if is_master else (PATH_COLOR if is_target else NODE_COLOR)
            size = 600 if is_master else 400

            ax.scatter(x, y, s=size * 2, color=color, alpha=0.1, zorder=3)
            ax.scatter(x, y, s=size, color=color, alpha=0.9, zorder=5,
                       edgecolors="white", linewidth=1.5)
            ax.text(x, y, node, ha="center", va="center",
                    fontsize=9 if is_master else 7.5,
                    fontweight="bold", color="#000000", zorder=6)

        # --- Info ---
        path_str = " → ".join(path) if path else "No path found"
        info = [
            f"Step {frame + 1}/{steps}",
            f"Route: {path_str}",
            f"Exploration: {exploration_rate:.0%}",
        ]
        if latency_history:
            info.append(f"Latency: {latency_history[-1]:.2f}")

        for idx, line in enumerate(info):
            ax.text(
                0.02, 0.97 - idx * 0.05, line,
                transform=ax.transAxes, fontsize=8.5, color=TEXT_COLOR,
                fontweight="bold", va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG,
                          edgecolor=GRID_COLOR, alpha=0.85),
                zorder=10,
            )

        ax.set_title(
            f"ACO Routing: M → {target_node}",
            fontsize=13, fontweight="bold", color=TEXT_COLOR, pad=12,
        )

    anim = FuncAnimation(fig, update, frames=steps, interval=int(pause_time * 1000),
                         repeat=False)

    if save_gif:
        import os
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        anim.save(output_path, writer="pillow", fps=2)
        print(f"Saved: {output_path}")

    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate a single ACO route.")
    parser.add_argument("--steps", type=int, default=30, help="Number of animation frames.")
    parser.add_argument("--pause-time", type=float, default=0.5, help="Pause between frames in seconds.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    parser.add_argument("--target", type=str, default="S6", help="Destination node.")
    parser.add_argument("--save", action="store_true", help="Save as GIF.")
    args = parser.parse_args()
    animate_network(
        steps=args.steps,
        pause_time=args.pause_time,
        seed=args.seed,
        target_node=args.target,
        save_gif=args.save,
    )


if __name__ == "__main__":
    main()
