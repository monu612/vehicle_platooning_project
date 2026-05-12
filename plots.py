import matplotlib.pyplot as plt

def plot_advanced():

    # Replace with your results if needed
    aco_pdr = 0.97
    baseline_pdr = 0.65

    aco_latency = [10, 12, 9, 14, 11, 13, 8, 15]
    baseline_latency = [7, 8, 9, 6, 10, 7, 8]

    aco_redundancy = [3, 2, 3, 4, 2, 3]
    baseline_redundancy = [2, 2, 2, 2, 2]

    # -------------------------
    # PDR GRAPH
    # -------------------------
    plt.figure()
    plt.bar(['ACO', 'Baseline'], [aco_pdr, baseline_pdr])
    plt.title("Packet Delivery Ratio (PDR)")
    plt.show()

    # -------------------------
    # LATENCY DISTRIBUTION
    # -------------------------
    plt.figure()
    plt.hist(aco_latency, alpha=0.6, label='ACO')
    plt.hist(baseline_latency, alpha=0.6, label='Baseline')
    plt.title("Latency Distribution")
    plt.legend()
    plt.show()

    # -------------------------
    # REDUNDANCY DISTRIBUTION
    # -------------------------
    plt.figure()
    plt.hist(aco_redundancy, alpha=0.6, label='ACO')
    plt.hist(baseline_redundancy, alpha=0.6, label='Baseline')
    plt.title("Redundancy Distribution")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    plot_advanced()