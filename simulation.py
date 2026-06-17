from __future__ import annotations

import argparse
import json
import random
from typing import Sequence

import networkx as nx

from aco import select_path, update_pheromone
from network import create_spider_web_topology


DESTINATIONS = ("S1", "S2", "S3", "S4", "S5", "S6")


def _validate_inputs(runs: int, failure_rate: float, congestion_factor: float) -> None:
    if runs < 0:
        raise ValueError("runs must be greater than or equal to 0.")
    if not 0.0 <= failure_rate <= 1.0:
        raise ValueError("failure_rate must be between 0 and 1.")
    if congestion_factor < 1.0:
        raise ValueError("congestion_factor must be greater than or equal to 1.")


def _path_latency(G: nx.Graph, path: list[str]) -> float:
    return sum(float(G[source][target].get("weight", 1.0)) for source, target in zip(path, path[1:]))


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _format_results(results: dict[str, float]) -> str:
    return "\n".join(
        [
            "",
            "===== FINAL ADVANCED RESULTS =====",
            f"PDR (ACO): {results['pdr_aco']:.3f}",
            f"PDR (Baseline): {results['pdr_base']:.3f}",
            f"ACO Avg Latency: {results['lat_aco']:.3f}",
            f"Baseline Avg Latency: {results['lat_base']:.3f}",
            f"ACO Avg Redundancy: {results['red_aco']:.3f}",
            f"Baseline Avg Redundancy: {results['red_base']:.3f}",
        ]
    )


def run_simulation(
    runs: int = 200,
    failure_rate: float = 0.2,
    congestion_factor: float = 1.5,
    seed: int | None = None,
    verbose: bool = True,
) -> dict[str, float]:
    """Run the ACO routing simulation and return aggregate metrics."""
    _validate_inputs(runs, failure_rate, congestion_factor)
    rng = random.Random(seed)

    G = create_spider_web_topology(rng=rng)

    packets_sent = 0
    packets_received_aco = 0
    packets_received_baseline = 0

    latency_aco = []
    latency_baseline = []

    redundancy_aco = []
    redundancy_baseline = []

    baseline_paths: dict[str, list[str] | None] = {}
    precomputed_paths: dict[str, list[list[str]]] = {}
    for destination in DESTINATIONS:
        try:
            baseline_paths[destination] = nx.shortest_path(G, "M", destination, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            baseline_paths[destination] = None

        try:
            precomputed_paths[destination] = list(nx.all_simple_paths(G, "M", destination, cutoff=4))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            precomputed_paths[destination] = []

    for i in range(runs):
        G_temp = G.copy()

        for u, v, edge in list(G_temp.edges(data=True)):
            reliability = float(edge.get("reliability", 1.0))
            failure_prob = failure_rate * (1 - reliability)
            if rng.random() < failure_prob:
                G_temp.remove_edge(u, v)

        for u, v, edge in G_temp.edges(data=True):
            edge["weight"] = float(edge.get("weight", 1.0)) * rng.uniform(0.9, 1.1)
            edge["congestion"] = float(edge.get("congestion", 1.0)) * rng.uniform(1.0, congestion_factor)

            reliability = float(edge.get("reliability", 1.0)) * rng.uniform(0.95, 1.05)
            edge["reliability"] = min(max(reliability, 0.5), 1.0)
            edge["pheromone"] = float(edge.get("pheromone", 1.0))

        exploration_rate = max(0.05, 0.3 * (1 - i / runs))

        for destination in DESTINATIONS:
            packets_sent += 1

            path = select_path(
                G_temp,
                "M",
                destination,
                exploration_rate=exploration_rate,
                rng=rng,
                precomputed_paths=precomputed_paths[destination],
            )

            if path:
                packets_received_aco += 1
                latency_aco.append(_path_latency(G_temp, path))
                redundancy_aco.append(len(path) - 1)
                update_pheromone(G, path)

            base_path = baseline_paths[destination]

            if base_path:
                valid = True
                total_latency_base = 0.0

                for source, target in zip(base_path, base_path[1:]):
                    if G_temp.has_edge(source, target):
                        total_latency_base += float(G_temp[source][target].get("weight", 1.0))
                    else:
                        valid = False
                        break

                if valid:
                    packets_received_baseline += 1
                    latency_baseline.append(total_latency_base)
                    redundancy_baseline.append(len(base_path) - 1)

    pdr_aco = packets_received_aco / packets_sent if packets_sent else 0
    pdr_base = packets_received_baseline / packets_sent if packets_sent else 0

    lat_aco = _mean(latency_aco)
    lat_base = _mean(latency_baseline)

    red_aco = _mean(redundancy_aco)
    red_base = _mean(redundancy_baseline)

    results = {
        "pdr_aco": pdr_aco,
        "pdr_base": pdr_base,
        "lat_aco": lat_aco,
        "lat_base": lat_base,
        "red_aco": red_aco,
        "red_base": red_base,
        "packets_sent": packets_sent,
        "packets_received_aco": packets_received_aco,
        "packets_received_baseline": packets_received_baseline,
    }

    if verbose:
        print(_format_results(results))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the vehicle platooning ACO simulation.")
    parser.add_argument("--runs", type=int, default=200, help="Number of simulation iterations.")
    parser.add_argument("--failure-rate", type=float, default=0.2, help="Base link failure rate, 0 to 1.")
    parser.add_argument("--congestion-factor", type=float, default=1.5, help="Maximum congestion multiplier.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for repeatable results.")
    parser.add_argument("--json", action="store_true", help="Print results as JSON.")
    args = parser.parse_args()

    results = run_simulation(
        runs=args.runs,
        failure_rate=args.failure_rate,
        congestion_factor=args.congestion_factor,
        seed=args.seed,
        verbose=not args.json,
    )

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
