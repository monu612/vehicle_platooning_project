from network import create_spider_web_topology
from aco import select_path

G = create_spider_web_topology()

path = select_path(G, "M", "S6")

print("Selected Path:", path)