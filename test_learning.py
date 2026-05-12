from network import create_spider_web_topology
from aco import select_path, update_pheromone

G = create_spider_web_topology()

for i in range(10):
    path = select_path(G, "M", "S6")
    update_pheromone(G, path)

    print(f"Run {i+1}: {path}")