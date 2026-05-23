from network import create_spider_web_topology
from aco import select_path, update_pheromone
import networkx as nx
import random

def run_simulation(runs=200, failure_rate=0.2, congestion_factor=1.5):

    # Create base graph (learning happens here)
    G = create_spider_web_topology()

    destinations = ["S1", "S2", "S3", "S4", "S5", "S6"]

    packets_sent = 0
    packets_received_aco = 0
    packets_received_baseline = 0

    latency_aco = []
    latency_baseline = []

    redundancy_aco = []
    redundancy_baseline = []

    # Precompute all possible simple paths from the base graph to avoid expensive recalculations
    precomputed_paths = {
        d: list(nx.all_simple_paths(G, "M", d, cutoff=4)) for d in destinations
    }

    # Static baseline paths (computed once)
    baseline_paths = {}
    for d in destinations:
        try:
            baseline_paths[d] = nx.shortest_path(G, "M", d, weight='weight')
        except:
            baseline_paths[d] = None

    for i in range(runs):

        # Temporary graph for dynamic changes
        G_temp = G.copy()

        # -------------------------
        # LINK FAILURES (based on reliability + failure_rate)
        # -------------------------
        for u, v in list(G_temp.edges()):
            failure_prob = failure_rate * (1 - G_temp[u][v]['reliability'])
            if random.random() < failure_prob:
                G_temp.remove_edge(u, v)

        # -------------------------
        # DYNAMIC NETWORK CONDITIONS
        # -------------------------
        for u, v in G_temp.edges():

            # Latency variation
            G_temp[u][v]['weight'] *= random.uniform(0.9, 1.1)

            # Congestion effect
            G_temp[u][v]['congestion'] *= random.uniform(1.0, congestion_factor)

            # Reliability fluctuation
            G_temp[u][v]['reliability'] *= random.uniform(0.95, 1.05)

            # Clamp reliability
            G_temp[u][v]['reliability'] = min(max(G_temp[u][v]['reliability'], 0.5), 1.0)

        # Exploration → Exploitation
        exploration_rate = max(0.05, 0.3 * (1 - i / runs))

        for d in destinations:

            packets_sent += 1

            # -------------------------
            # ACO SYSTEM
            # -------------------------
            path = select_path(
                G_temp, "M", d,
                exploration_rate=exploration_rate,
                precomputed_paths=precomputed_paths[d]
            )

            if path:
                packets_received_aco += 1

                total_latency = 0
                for j in range(len(path) - 1):
                    total_latency += G_temp[path[j]][path[j+1]]['weight']

                latency_aco.append(total_latency)
                redundancy_aco.append(len(path) - 1)

                # Learn on base graph
                update_pheromone(G, path)

            # -------------------------
            # BASELINE SYSTEM (static path)
            # -------------------------
            base_path = baseline_paths[d]

            if base_path:
                valid = True
                total_latency_base = 0

                for j in range(len(base_path) - 1):
                    u, v = base_path[j], base_path[j+1]

                    if G_temp.has_edge(u, v):
                        total_latency_base += G_temp[u][v]['weight']
                    else:
                        valid = False
                        break

                if valid:
                    packets_received_baseline += 1
                    latency_baseline.append(total_latency_base)
                    redundancy_baseline.append(len(base_path) - 1)

    # -------------------------
    # SAFE CALCULATIONS
    # -------------------------
    pdr_aco = packets_received_aco / packets_sent if packets_sent else 0
    pdr_base = packets_received_baseline / packets_sent if packets_sent else 0

    lat_aco = sum(latency_aco) / len(latency_aco) if latency_aco else 0
    lat_base = sum(latency_baseline) / len(latency_baseline) if latency_baseline else 0

    red_aco = sum(redundancy_aco) / len(redundancy_aco) if redundancy_aco else 0
    red_base = sum(redundancy_baseline) / len(redundancy_baseline) if redundancy_baseline else 0

    # -------------------------
    # PRINT RESULTS (for terminal)
    # -------------------------
    print("\n===== FINAL ADVANCED RESULTS =====")
    print(f"PDR (ACO): {pdr_aco:.3f}")
    print(f"PDR (Baseline): {pdr_base:.3f}")
    print(f"ACO Avg Latency: {lat_aco:.3f}")
    print(f"Baseline Avg Latency: {lat_base:.3f}")
    print(f"ACO Avg Redundancy: {red_aco:.3f}")
    print(f"Baseline Avg Redundancy: {red_base:.3f}")

    # -------------------------
    # RETURN (for UI)
    # -------------------------
    return {
        "pdr_aco": pdr_aco,
        "pdr_base": pdr_base,
        "lat_aco": lat_aco,
        "lat_base": lat_base,
        "red_aco": red_aco,
        "red_base": red_base
    }


if __name__ == "__main__":
    run_simulation()