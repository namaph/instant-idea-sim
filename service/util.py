import logging
from typing import Dict, Optional, Any

import matplotlib.pyplot as plt
import networkx as nx
import redis
import seaborn as sns

from .grid import Grid

def get_conn_pool(host:str, port:str, db:int):
  return redis.ConnectionPool(
    host=host,
    port=port,
    db=db
  )

class get_conn():
  def __init__(self, pool):
    self.r = redis.StrictRedis(connection_pool=pool)

  def __call__(self) -> Optional[Any]:
    ret = None
    try:
      self.r.ping()
      ret = self.r
    except redis.exceptions.ConnectionError as exc:
      logging.debug("No Connection Error")
      logging.debug(exc)
      ret = None
    return ret
  
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