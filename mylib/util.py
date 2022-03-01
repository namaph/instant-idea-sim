from typing import Dict

import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

from .visualizer import Grid

def get_neighbor(graph, label) -> Dict[int, float]:
  res = {}
  for i in graph[label]:
    t, v = graph.nodes[i].values()
    if t not in res.keys():
      res[t] = v
    else:
      res[t] += v
  return res
  
def plot_graph(graph, fname="./graph.png"):
  info = nx.get_node_attributes(graph, 'type') 
  labels = {k: f'{k}:{v}' for k, v in info.items()}
  cmap = {'1': 'green', '2': 'red', '3': 'blue'}
  col = [cmap[v] for k, v in info.items()]
  nx.draw(graph, with_labels=True, labels=labels, font_size=10, font_color="w", node_size=500, node_color=col)
  plt.savefig(fname)

def plot_grid(graph, pos, cont, fname="./grid.png"):
  grid = Grid(pos)
  grid.set_attr(nx.get_node_attributes(graph, cont).values())
  f, a = plt.subplots(figsize=(10, 10))
  sns.heatmap(grid.grid, ax=a, cbar=False)
  f.savefig(fname)