from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from typing import Sequence

import networkx as nx

from aco import (
    select_path, update_pheromone, evaporate_all, deposit_elite,
    get_network_state, adaptive_parameters
)
from network import create_spider_web_topology


DESTINATIONS = ("S1", "S2", "S3", "S4", "S5", "S6")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class SimulationConfig:
    """All tuneable parameters in one place."""
    runs: int = 200
    failure_rate: float = 0.2
    congestion_factor: float = 1.5
    seed: int | None = None
    exploration_start: float = 0.3
    exploration_end: float = 0.05
    elite: bool = True


# ---------------------------------------------------------------------------
# Per-iteration metrics
# ---------------------------------------------------------------------------

@dataclass
class IterationMetrics:
    """Metrics for a single simulation iteration."""
    pdr_aco: float = 0.0
    pdr_base: float = 0.0
    pdr_greedy: float = 0.0
    lat_aco: float = 0.0
    lat_base: float = 0.0
    lat_greedy: float = 0.0


@dataclass
class SimulationResult:
    """Aggregate *and* per-iteration results."""
    # Aggregates
    pdr_aco: float = 0.0
    pdr_base: float = 0.0
    pdr_greedy: float = 0.0
    lat_aco: float = 0.0
    lat_base: float = 0.0
    lat_greedy: float = 0.0
    red_aco: float = 0.0
    red_base: float = 0.0
    red_greedy: float = 0.0
    packets_sent: int = 0
    packets_received_aco: int = 0
    packets_received_baseline: int = 0
    packets_received_greedy: int = 0

    # Per-iteration series (for convergence plots)
    history: list[IterationMetrics] = field(default_factory=list)

    def as_dict(self) -> dict[str, float | int]:
        """Return aggregate metrics as a flat dict (backwards compatible)."""
        return {
            "pdr_aco": self.pdr_aco,
            "pdr_base": self.pdr_base,
            "pdr_greedy": self.pdr_greedy,
            "lat_aco": self.lat_aco,
            "lat_base": self.lat_base,
            "lat_greedy": self.lat_greedy,
            "red_aco": self.red_aco,
            "red_base": self.red_base,
            "red_greedy": self.red_greedy,
            "packets_sent": self.packets_sent,
            "packets_received_aco": self.packets_received_aco,
            "packets_received_baseline": self.packets_received_baseline,
            "packets_received_greedy": self.packets_received_greedy,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_inputs(runs: int, failure_rate: float, congestion_factor: float) -> None:
    if runs < 0:
        raise ValueError("runs must be greater than or equal to 0.")
    if not 0.0 <= failure_rate <= 1.0:
        raise ValueError("failure_rate must be between 0 and 1.")
    if congestion_factor < 1.0:
        raise ValueError("congestion_factor must be greater than or equal to 1.")


def _path_latency(G: nx.Graph, path: list[str]) -> float:
    return sum(float(G[s][t].get("weight", 1.0)) for s, t in zip(path, path[1:]))


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _greedy_path(G: nx.Graph, source: str, target: str) -> list[str] | None:
    """Greedy forwarding: always pick the neighbour with the lowest edge weight
    that hasn't been visited yet.  Returns None if stuck."""
    visited: set[str] = set()
    path = [source]
    current = source

    while current != target:
        visited.add(current)
        neighbours = [
            (n, float(G[current][n].get("weight", 1.0)))
            for n in G.neighbors(current)
            if n not in visited
        ]
        if not neighbours:
            return None
        # pick lowest-weight neighbour
        next_node = min(neighbours, key=lambda x: x[1])[0]
        path.append(next_node)
        current = next_node

    return path


def _format_results(result: SimulationResult) -> str:
    return "\n".join(
        [
            "",
            "===== FINAL ADVANCED RESULTS =====",
            f"PDR (ACO):      {result.pdr_aco:.3f}",
            f"PDR (Baseline): {result.pdr_base:.3f}",
            f"PDR (Greedy):   {result.pdr_greedy:.3f}",
            f"ACO Avg Latency:      {result.lat_aco:.3f}",
            f"Baseline Avg Latency: {result.lat_base:.3f}",
            f"Greedy Avg Latency:   {result.lat_greedy:.3f}",
            f"ACO Avg Redundancy:      {result.red_aco:.3f}",
            f"Baseline Avg Redundancy: {result.red_base:.3f}",
            f"Greedy Avg Redundancy:   {result.red_greedy:.3f}",
        ]
    )


# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------

def run_simulation(
    runs: int = 200,
    failure_rate: float = 0.2,
    congestion_factor: float = 1.5,
    seed: int | None = None,
    verbose: bool = True,
    config: SimulationConfig | None = None,
) -> SimulationResult:
    """Run the ACO routing simulation and return aggregate + per-iteration metrics."""

    if config is None:
        config = SimulationConfig(
            runs=runs,
            failure_rate=failure_rate,
            congestion_factor=congestion_factor,
            seed=seed,
        )
    else:
        runs = config.runs
        failure_rate = config.failure_rate
        congestion_factor = config.congestion_factor
        seed = config.seed

    _validate_inputs(runs, failure_rate, congestion_factor)
    rng = random.Random(seed)

    G = create_spider_web_topology(rng=rng)

    packets_sent = 0
    packets_received_aco = 0
    packets_received_baseline = 0
    packets_received_greedy = 0

    latency_aco: list[float] = []
    latency_baseline: list[float] = []
    latency_greedy: list[float] = []

    redundancy_aco: list[float] = []
    redundancy_baseline: list[float] = []
    redundancy_greedy: list[float] = []

    history: list[IterationMetrics] = []

    # Static baseline: pre-compute shortest paths once.
    # Pre-compute all simple paths for ACO to avoid nx.all_simple_paths overhead in each iteration
    aco_paths: dict[str, list[list[str]]] = {}
    for destination in DESTINATIONS:
        try:
            aco_paths[destination] = list(nx.all_simple_paths(G, "M", destination, cutoff=4))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            aco_paths[destination] = []
    baseline_paths: dict[str, list[str] | None] = {}
    for destination in DESTINATIONS:
        try:
            baseline_paths[destination] = nx.shortest_path(G, "M", destination, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            baseline_paths[destination] = None

    # Track global best for elite ant.
    global_best_path: list[str] | None = None
    global_best_latency = float("inf")

    for i in range(runs):
        # Create a copy with per-iteration perturbations.
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

        # --- Network state and adaptive parameters ---
        avg_cong, avg_rel, instab = get_network_state(G_temp)
        dyn_alpha, dyn_beta, dyn_rho = adaptive_parameters(avg_cong, avg_rel, failure_rate)

        # --- Global pheromone evaporation ---
        # Evaporate on the master graph using the dynamic rho
        evaporate_all(G, rho=dyn_rho)

        exploration_rate = max(
            config.exploration_end,
            config.exploration_start * (1 - i / runs),
        )

        # --- Per-iteration counters ---
        iter_sent = 0
        iter_recv_aco = 0
        iter_recv_base = 0
        iter_recv_greedy = 0
        iter_lat_aco: list[float] = []
        iter_lat_base: list[float] = []
        iter_lat_greedy: list[float] = []

        for destination in DESTINATIONS:
            packets_sent += 1
            iter_sent += 1

            # --- ACO path ---
            path = select_path(
                G_temp,
                "M",
                destination,
                alpha=dyn_alpha,
                beta=dyn_beta,
                exploration_rate=exploration_rate,
                rng=rng,
                precomputed_paths=aco_paths[destination],
            )

            if path:
                packets_received_aco += 1
                iter_recv_aco += 1
                lat = _path_latency(G_temp, path)
                latency_aco.append(lat)
                iter_lat_aco.append(lat)
                redundancy_aco.append(len(path) - 1)
                # Deposit pheromone on the *master* graph.
                update_pheromone(G, path, rho=dyn_rho)

                # Track global best for elite deposit.
                if lat < global_best_latency:
                    global_best_latency = lat
                    global_best_path = list(path)

            # --- Static baseline ---
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
                    iter_recv_base += 1
                    latency_baseline.append(total_latency_base)
                    iter_lat_base.append(total_latency_base)
                    redundancy_baseline.append(len(base_path) - 1)

            # --- Greedy baseline ---
            greedy_path = _greedy_path(G_temp, "M", destination)
            if greedy_path:
                packets_received_greedy += 1
                iter_recv_greedy += 1
                g_lat = _path_latency(G_temp, greedy_path)
                latency_greedy.append(g_lat)
                iter_lat_greedy.append(g_lat)
                redundancy_greedy.append(len(greedy_path) - 1)

        # Elite ant bonus on the master graph.
        if config.elite:
            deposit_elite(G, global_best_path)

        # Record per-iteration metrics.
        history.append(IterationMetrics(
            pdr_aco=iter_recv_aco / iter_sent if iter_sent else 0,
            pdr_base=iter_recv_base / iter_sent if iter_sent else 0,
            pdr_greedy=iter_recv_greedy / iter_sent if iter_sent else 0,
            lat_aco=_mean(iter_lat_aco),
            lat_base=_mean(iter_lat_base),
            lat_greedy=_mean(iter_lat_greedy),
        ))

    result = SimulationResult(
        pdr_aco=packets_received_aco / packets_sent if packets_sent else 0,
        pdr_base=packets_received_baseline / packets_sent if packets_sent else 0,
        pdr_greedy=packets_received_greedy / packets_sent if packets_sent else 0,
        lat_aco=_mean(latency_aco),
        lat_base=_mean(latency_baseline),
        lat_greedy=_mean(latency_greedy),
        red_aco=_mean(redundancy_aco),
        red_base=_mean(redundancy_baseline),
        red_greedy=_mean(redundancy_greedy),
        packets_sent=packets_sent,
        packets_received_aco=packets_received_aco,
        packets_received_baseline=packets_received_baseline,
        packets_received_greedy=packets_received_greedy,
        history=history,
    )

    if verbose:
        print(_format_results(result))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the vehicle platooning ACO simulation.")
    parser.add_argument("--runs", type=int, default=200, help="Number of simulation iterations.")
    parser.add_argument("--failure-rate", type=float, default=0.2, help="Base link failure rate, 0 to 1.")
    parser.add_argument("--congestion-factor", type=float, default=1.5, help="Maximum congestion multiplier.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for repeatable results.")
    parser.add_argument("--json", action="store_true", help="Print results as JSON.")
    args = parser.parse_args()

    result = run_simulation(
        runs=args.runs,
        failure_rate=args.failure_rate,
        congestion_factor=args.congestion_factor,
        seed=args.seed,
        verbose=not args.json,
    )

    if args.json:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
