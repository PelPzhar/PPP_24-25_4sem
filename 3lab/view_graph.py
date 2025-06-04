import networkx as nx
import matplotlib.pyplot as plt

graphml_file = "graph_eb913242-7057-4dbd-9f05-35c4ef6b63d2.graphml"

G = nx.read_graphml(graphml_file)

plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=500, node_color="lightblue", font_size=8, arrows=True)
plt.title("Graph of Website Links")
plt.show()