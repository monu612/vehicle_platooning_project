from network import create_spider_web_topology

G = create_spider_web_topology()

print("Nodes:", G.nodes())
print("Edges:", G.edges(data=True))