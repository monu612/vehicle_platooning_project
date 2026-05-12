import matplotlib.pyplot as plt

def plot_final_results():

    aco_pdr = 0.97
    baseline_pdr = 0.65

    aco_latency = 13.8
    baseline_latency = 10.4

    aco_redundancy = 3.2
    baseline_redundancy = 2.0

    methods = ['ACO', 'Baseline']

    # -------------------------
    # 1. PDR GRAPH
    # -------------------------
    plt.figure(figsize=(6,4))
    pdr_values = [aco_pdr, baseline_pdr]

    plt.bar(methods, pdr_values)

    for i, v in enumerate(pdr_values):
        plt.text(i, v + 0.02, f"{v:.2f}", ha='center', fontsize=10)

    plt.title("Packet Delivery Ratio (PDR)")
    plt.ylabel("PDR")
    plt.ylim(0, 1.1)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("pdr_graph.png", dpi=300)
    plt.show()

    # -------------------------
    # 2. LATENCY GRAPH
    # -------------------------
    plt.figure(figsize=(6,4))
    latency_values = [aco_latency, baseline_latency]

    plt.bar(methods, latency_values)

    for i, v in enumerate(latency_values):
        plt.text(i, v + 0.5, f"{v:.2f}", ha='center', fontsize=10)

    plt.title("Average Latency Comparison")
    plt.ylabel("Latency (ms)")
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("latency_graph.png", dpi=300)
    plt.show()

    # -------------------------
    # 3. REDUNDANCY GRAPH
    # -------------------------
    plt.figure(figsize=(6,4))
    redundancy_values = [aco_redundancy, baseline_redundancy]

    plt.bar(methods, redundancy_values)

    for i, v in enumerate(redundancy_values):
        plt.text(i, v + 0.2, f"{v:.2f}", ha='center', fontsize=10)

    plt.title("Average Redundancy (Hops)")
    plt.ylabel("Number of Hops")
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("redundancy_graph.png", dpi=300)
    plt.show()

    # -------------------------
    # 4. DISTRIBUTION GRAPH
    # -------------------------
    # Example distributions (replace later if needed)
    aco_latency_dist = [12, 14, 11, 15, 13, 10, 16, 12]
    baseline_latency_dist = [8, 9, 7, 10, 8, 9, 7]

    plt.figure(figsize=(6,4))

    plt.hist(aco_latency_dist, alpha=0.6, label='ACO')
    plt.hist(baseline_latency_dist, alpha=0.6, label='Baseline')

    plt.title("Latency Distribution")
    plt.xlabel("Latency")
    plt.ylabel("Frequency")
    plt.legend()

    plt.tight_layout()
    plt.savefig("latency_distribution.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    plot_final_results()