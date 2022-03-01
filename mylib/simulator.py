from typing import Callable

from numpy.typing import NDArray
import networkx as nx

from . import const as C

nGraph = nx.classes.graph.Graph

class SimCon():
  init_state: nGraph

  def __init__(self, labels, topology, values):
    self.init_state = nx.Graph()
    for l, v in zip(labels, values):
      self.init_state.add_node(l, type=v, value=C.init_val)
    self.init_state.add_edges_from([[labels[t[0]], labels[t[1]]] for t in topology])

  def run_sim(self, n_step:int, f_update: Callable[[nGraph], nGraph]):
    state = self.init_state
    hist = [state]
    for _ in range(n_step):
      state = f_update(state)
      hist.append(state)
    
    return hist