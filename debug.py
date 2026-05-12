import networkx as nx
from network import create_spider_web_topology

G = create_spider_web_topology()

print("Is graph connected:", nx.is_connected(G))

print("\nAll edges:")
for edge in G.edges():
    print(edge)