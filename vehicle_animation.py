from __future__ import annotations

import argparse
import random

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from matplotlib.animation import FuncAnimation

from network import create_spider_web_topology
from aco import select_path, update_pheromone, evaporate_all, get_network_state, adaptive_parameters


# --- Dark palette ---
BG_COLOR = "#0f0f0f"
CARD_BG = "#1e1e2e"
MASTER_COLOR = "#00ff88"
NODE_COLOR = "#00d4ff"
EDGE_DEFAULT = "#333355"
PATH_COLOR = "#ff5577"
TRAIL_COLOR = "#ffaa00"
TEXT_COLOR = "#ffffff"
PHEROMONE_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "pheromone", ["#1e1e2e", "#00d4ff", "#00ff88"]
)


def animate_realistic(
    steps: int = 60,
    seed: int | None = None,
    save_gif: bool = True,
    output_path: str = "output/platoon_animation.gif",
) -> None:
    rng = random.Random(seed)
    G = create_spider_web_topology(rng=rng)
    nodes = list(G.nodes())

    # Precompute paths for ACO
    aco_paths: dict[str, list[list[str]]] = {}
    for dest in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        try:
            aco_paths[dest] = list(nx.all_simple_paths(G, "M", dest, cutoff=4))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            aco_paths[dest] = []

    # Compute a nice initial layout, then perturb each frame.
    pos = nx.spring_layout(G, seed=42, k=2.5)
    # Convert to mutable lists.
    pos = {n: [float(p[0]) * 5 + 5, float(p[1]) * 5 + 5] for n, p in pos.items()}

    path_history: list[list[str]] = []

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG_COLOR)

    def update(frame: int):
        ax.clear()
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 11)
        ax.set_aspect("equal")
        ax.axis("off")

        # --- Gentle node drift ---
        for node in pos:
            pos[node][0] += rng.uniform(-0.12, 0.12)
            pos[node][1] += rng.uniform(-0.12, 0.12)
            pos[node][0] = max(0, min(10, pos[node][0]))
            pos[node][1] = max(0, min(10, pos[node][1]))

        # --- Perturb edge attributes ---
        for u, v in G.edges():
            G[u][v]["weight"] = max(0.5, G[u][v]["weight"] * rng.uniform(0.93, 1.07))
            rel = G[u][v]["reliability"] * rng.uniform(0.97, 1.03)
            G[u][v]["reliability"] = min(max(rel, 0.5), 1.0)
            G[u][v]["congestion"] = max(0.3, G[u][v]["congestion"] * rng.uniform(0.9, 1.1))

        # --- Network state and adaptive parameters ---
        avg_cong, avg_rel, instab = get_network_state(G)
        dyn_alpha, dyn_beta, dyn_rho = adaptive_parameters(avg_cong, avg_rel, failure_rate=0.0)

        evaporate_all(G, rho=dyn_rho)

        # --- ACO: select paths ---
        exploration_rate = max(0.05, 0.3 * (1 - frame / steps))
        current_paths: list[list[str]] = []
        for target in ["S1", "S2", "S3", "S4", "S5", "S6"]:
            path = select_path(G, "M", target, alpha=dyn_alpha, beta=dyn_beta, exploration_rate=exploration_rate, rng=rng, precomputed_paths=aco_paths[target])
            if path:
                update_pheromone(G, path, rho=dyn_rho)
                current_paths.append(path)
                path_history.append(path)

        # ---------------------------
        # DRAW EDGES: color by pheromone intensity
        # ---------------------------
        pheromone_vals = [G[u][v].get("pheromone", 1.0) for u, v in G.edges()]
        p_min = min(pheromone_vals) if pheromone_vals else 0.1
        p_max = max(pheromone_vals) if pheromone_vals else 10.0
        if p_max == p_min:
            p_max = p_min + 1

        for u, v in G.edges():
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            p = G[u][v].get("pheromone", 1.0)
            norm = (p - p_min) / (p_max - p_min)
            color = PHEROMONE_CMAP(norm)
            width = 1.0 + norm * 3.0
            ax.plot(x, y, color=color, linewidth=width, alpha=0.6, zorder=1)

        # ---------------------------
        # DRAW PATH TRAILS (faded recent history)
        # ---------------------------
        trail_slice = path_history[-12:]
        for idx, old_path in enumerate(trail_slice):
            alpha = 0.05 + 0.1 * (idx / max(len(trail_slice), 1))
            for j in range(len(old_path) - 1):
                u, v = old_path[j], old_path[j + 1]
                if u in pos and v in pos:
                    ax.plot(
                        [pos[u][0], pos[v][0]],
                        [pos[u][1], pos[v][1]],
                        color=TRAIL_COLOR, linewidth=1.5, alpha=alpha, zorder=2,
                    )

        # ---------------------------
        # DRAW CURRENT PATHS (bold)
        # ---------------------------
        for path in current_paths:
            for j in range(len(path) - 1):
                u, v = path[j], path[j + 1]
                ax.plot(
                    [pos[u][0], pos[v][0]],
                    [pos[u][1], pos[v][1]],
                    color=PATH_COLOR, linewidth=3, alpha=0.9, zorder=4,
                )

        # ---------------------------
        # DRAW NODES
        # ---------------------------
        for node in nodes:
            x, y = pos[node]
            is_master = node == "M"
            color = MASTER_COLOR if is_master else NODE_COLOR
            size = 700 if is_master else 450

            # Glow effect
            ax.scatter(x, y, s=size * 2.5, color=color, alpha=0.08, zorder=3)
            ax.scatter(x, y, s=size * 1.5, color=color, alpha=0.15, zorder=3)
            ax.scatter(x, y, s=size, color=color, alpha=0.9, zorder=5,
                       edgecolors="white", linewidth=1.5)
            ax.text(x, y, node, ha="center", va="center",
                    fontsize=10 if is_master else 8,
                    fontweight="bold", color="#000000", zorder=6)

        # ---------------------------
        # INFO PANEL
        # ---------------------------
        delivered = len(current_paths)
        total = 6
        avg_pheromone = sum(pheromone_vals) / len(pheromone_vals) if pheromone_vals else 0

        info_lines = [
            f"Step {frame + 1}/{steps}",
            f"Delivered: {delivered}/{total}",
            f"Exploration: {exploration_rate:.0%}",
            f"Avg Pheromone: {avg_pheromone:.2f}",
        ]

        for idx, line in enumerate(info_lines):
            ax.text(
                0.02, 0.98 - idx * 0.05, line,
                transform=ax.transAxes,
                fontsize=9, color=TEXT_COLOR, fontweight="bold",
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG,
                          edgecolor=EDGE_DEFAULT, alpha=0.85),
                zorder=10,
            )

        # Title
        ax.set_title(
            "ACO Vehicle Platooning — Real-Time Routing",
            fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=15,
        )

        # Legend
        legend_items = [
            ("●", MASTER_COLOR, "Master Node"),
            ("●", NODE_COLOR, "Follower Node"),
            ("—", PATH_COLOR, "Current Route"),
            ("—", TRAIL_COLOR, "Recent Trail"),
        ]
        for idx, (marker, color, label) in enumerate(legend_items):
            ax.text(
                0.98, 0.98 - idx * 0.045, f"{marker} {label}",
                transform=ax.transAxes, fontsize=8, color=color,
                ha="right", va="top", fontweight="bold",
                zorder=10,
            )

    anim = FuncAnimation(fig, update, frames=steps, interval=400, repeat=False)

    if save_gif:
        import os
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        print(f"Saving animation to {output_path}...")
        anim.save(output_path, writer="pillow", fps=3)
        print(f"Saved: {output_path}")

    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate the vehicle platooning topology.")
    parser.add_argument("--steps", type=int, default=60, help="Number of animation frames.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    parser.add_argument("--no-save", action="store_true", help="Don't save GIF.")
    args = parser.parse_args()
    animate_realistic(steps=args.steps, seed=args.seed, save_gif=not args.no_save)


if __name__ == "__main__":
    main()
