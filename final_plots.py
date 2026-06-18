from __future__ import annotations

import argparse
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from simulation import run_simulation


OUTPUT_DIR = Path("output")

# --- Dark theme palette ---
BG_COLOR = "#0f0f0f"
CARD_BG = "#1e1e2e"
ACO_COLOR = "#00d4ff"
BASE_COLOR = "#ffaa00"
GREEDY_COLOR = "#ff5577"
GRID_COLOR = "#333344"
TEXT_COLOR = "#ffffff"


def _apply_dark_style(fig: plt.Figure, axes) -> None:
    """Apply consistent dark styling to a figure and its axes."""
    fig.patch.set_facecolor(BG_COLOR)
    if not hasattr(axes, "__iter__"):
        axes = [axes]
    for ax in axes:
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT_COLOR, labelsize=9)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=GRID_COLOR)


def _save_bar_chart(
    title: str,
    ylabel: str,
    labels: list[str],
    values: list[float],
    colors: list[str],
    output_file: Path,
    y_limit: tuple[float, float] | None = None,
) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    _apply_dark_style(fig, ax)

    bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.5,
                  zorder=3)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + (max(values) * 0.02),
            f"{height:.3f}",
            ha="center", va="bottom", fontsize=11,
            fontweight="bold", color=TEXT_COLOR,
        )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=11)
    if y_limit:
        ax.set_ylim(*y_limit)

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_file


def _save_convergence_plot(
    result,
    output_file: Path,
) -> Path:
    """Plot PDR and latency per iteration to show ACO learning over time."""
    history = result.history
    iters = list(range(1, len(history) + 1))

    # Smooth with a rolling window
    window = max(1, len(history) // 20)

    def smooth(data):
        arr = np.array(data, dtype=float)
        kernel = np.ones(window) / window
        return np.convolve(arr, kernel, mode="valid")

    pdr_aco = smooth([h.pdr_aco for h in history])
    pdr_base = smooth([h.pdr_base for h in history])
    pdr_greedy = smooth([h.pdr_greedy for h in history])
    x = np.arange(1, len(pdr_aco) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    _apply_dark_style(fig, [ax1, ax2])

    # PDR convergence
    ax1.plot(x, pdr_aco, color=ACO_COLOR, linewidth=2, label="ACO")
    ax1.plot(x, pdr_base, color=BASE_COLOR, linewidth=2, label="Shortest Path")
    ax1.plot(x, pdr_greedy, color=GREEDY_COLOR, linewidth=2, label="Greedy")
    ax1.fill_between(x, pdr_aco, alpha=0.15, color=ACO_COLOR)
    ax1.set_title("Packet Delivery Rate — Convergence", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("PDR")
    ax1.set_ylim(-0.05, 1.1)
    ax1.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # Latency convergence
    lat_aco = smooth([h.lat_aco for h in history])
    lat_base = smooth([h.lat_base for h in history])
    lat_greedy = smooth([h.lat_greedy for h in history])
    x2 = np.arange(1, len(lat_aco) + 1)

    ax2.plot(x2, lat_aco, color=ACO_COLOR, linewidth=2, label="ACO")
    ax2.plot(x2, lat_base, color=BASE_COLOR, linewidth=2, label="Shortest Path")
    ax2.plot(x2, lat_greedy, color=GREEDY_COLOR, linewidth=2, label="Greedy")
    ax2.fill_between(x2, lat_aco, alpha=0.15, color=ACO_COLOR)
    ax2.set_title("Average Latency — Convergence", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Latency")
    ax2.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_file


def _save_sensitivity_plot(
    runs: int,
    seed: int | None,
    output_file: Path,
) -> Path:
    """Vary failure_rate and plot its impact on PDR for all three algorithms."""
    failure_rates = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
    pdr_aco = []
    pdr_base = []
    pdr_greedy = []

    for fr in failure_rates:
        r = run_simulation(runs=runs, failure_rate=fr, seed=seed, verbose=False)
        pdr_aco.append(r.pdr_aco)
        pdr_base.append(r.pdr_base)
        pdr_greedy.append(r.pdr_greedy)

    fig, ax = plt.subplots(figsize=(8, 5))
    _apply_dark_style(fig, ax)

    ax.plot(failure_rates, pdr_aco, "o-", color=ACO_COLOR, linewidth=2.5,
            markersize=7, label="ACO", zorder=3)
    ax.plot(failure_rates, pdr_base, "s--", color=BASE_COLOR, linewidth=2,
            markersize=6, label="Shortest Path", zorder=3)
    ax.plot(failure_rates, pdr_greedy, "^--", color=GREEDY_COLOR, linewidth=2,
            markersize=6, label="Greedy", zorder=3)

    ax.fill_between(failure_rates, pdr_aco, alpha=0.1, color=ACO_COLOR)

    ax.set_title("PDR vs. Failure Rate — Sensitivity Analysis",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Link Failure Rate", fontsize=11)
    ax.set_ylabel("Packet Delivery Rate", fontsize=11)
    ax.set_ylim(-0.05, 1.1)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR,
              fontsize=10, loc="lower left")

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_file


def _save_latency_distribution(
    runs: int,
    samples: int,
    seed: int | None,
    output_file: Path,
) -> Path:
    rng = random.Random(seed)
    aco_latency = []
    baseline_latency = []
    greedy_latency = []

    for _ in range(samples):
        sample_seed = rng.randrange(1_000_000_000)
        result = run_simulation(runs=runs, seed=sample_seed, verbose=False)
        aco_latency.append(result.lat_aco)
        baseline_latency.append(result.lat_base)
        greedy_latency.append(result.lat_greedy)

    fig, ax = plt.subplots(figsize=(8, 5))
    _apply_dark_style(fig, ax)

    ax.hist(aco_latency, alpha=0.7, label="ACO", color=ACO_COLOR, edgecolor="none")
    ax.hist(baseline_latency, alpha=0.55, label="Shortest Path", color=BASE_COLOR,
            edgecolor="none")
    ax.hist(greedy_latency, alpha=0.45, label="Greedy", color=GREEDY_COLOR,
            edgecolor="none")

    ax.set_title("Latency Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Average Latency", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=10)

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_file


def plot_final_results(
    runs: int = 200,
    samples: int = 25,
    seed: int | None = 42,
    output_dir: Path | str = OUTPUT_DIR,
) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    result = run_simulation(runs=runs, seed=seed, verbose=False)

    labels = ["ACO", "Shortest Path", "Greedy"]
    colors = [ACO_COLOR, BASE_COLOR, GREEDY_COLOR]

    files = [
        _save_bar_chart(
            "Packet Delivery Ratio (PDR)",
            "PDR",
            labels,
            [result.pdr_aco, result.pdr_base, result.pdr_greedy],
            colors,
            output_path / "pdr_graph.png",
            y_limit=(0, 1.15),
        ),
        _save_bar_chart(
            "Average Latency Comparison",
            "Latency",
            labels,
            [result.lat_aco, result.lat_base, result.lat_greedy],
            colors,
            output_path / "latency_graph.png",
        ),
        _save_bar_chart(
            "Average Redundancy (Hop Count)",
            "Number of Hops",
            labels,
            [result.red_aco, result.red_base, result.red_greedy],
            colors,
            output_path / "redundancy_graph.png",
        ),
        _save_convergence_plot(
            result,
            output_path / "convergence.png",
        ),
        _save_sensitivity_plot(
            runs=runs,
            seed=seed,
            output_file=output_path / "sensitivity.png",
        ),
        _save_latency_distribution(
            runs=runs,
            samples=samples,
            seed=seed,
            output_file=output_path / "latency_distribution.png",
        ),
    ]
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate simulation result plots.")
    parser.add_argument("--runs", type=int, default=200, help="Simulation runs used per sample.")
    parser.add_argument("--samples", type=int, default=25, help="Samples used for latency distribution.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatable plots.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for generated images.")
    args = parser.parse_args()

    files = plot_final_results(
        runs=args.runs,
        samples=args.samples,
        seed=args.seed,
        output_dir=args.output_dir,
    )

    for file in files:
        print(file)


if __name__ == "__main__":
    main()
