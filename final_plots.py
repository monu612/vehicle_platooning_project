from __future__ import annotations

import argparse
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from simulation import run_simulation


OUTPUT_DIR = Path("output")


def _save_bar_chart(
    title: str,
    ylabel: str,
    values: list[float],
    output_file: Path,
    y_limit: tuple[float, float] | None = None,
) -> Path:
    fig, axis = plt.subplots(figsize=(6, 4))
    bars = axis.bar(["ACO", "Baseline"], values, color=["#0077b6", "#f77f00"])

    for bar in bars:
        height = bar.get_height()
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    if y_limit:
        axis.set_ylim(*y_limit)

    fig.tight_layout()
    fig.savefig(output_file, dpi=300)
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

    for _ in range(samples):
        sample_seed = rng.randrange(1_000_000_000)
        result = run_simulation(runs=runs, seed=sample_seed, verbose=False)
        aco_latency.append(result["lat_aco"])
        baseline_latency.append(result["lat_base"])

    fig, axis = plt.subplots(figsize=(6, 4))
    axis.hist(aco_latency, alpha=0.65, label="ACO")
    axis.hist(baseline_latency, alpha=0.65, label="Baseline")
    axis.set_title("Latency Distribution")
    axis.set_xlabel("Average latency")
    axis.set_ylabel("Frequency")
    axis.legend()

    fig.tight_layout()
    fig.savefig(output_file, dpi=300)
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

    files = [
        _save_bar_chart(
            "Packet Delivery Ratio (PDR)",
            "PDR",
            [result["pdr_aco"], result["pdr_base"]],
            output_path / "pdr_graph.png",
            y_limit=(0, 1.1),
        ),
        _save_bar_chart(
            "Average Latency Comparison",
            "Latency",
            [result["lat_aco"], result["lat_base"]],
            output_path / "latency_graph.png",
        ),
        _save_bar_chart(
            "Average Redundancy",
            "Number of hops",
            [result["red_aco"], result["red_base"]],
            output_path / "redundancy_graph.png",
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
