import pickle
from typing import Callable

import networkx as nx

from . import types as T
from .datastore import Store


class SimCon():
  init_state: T.nGraph

  def __init__(self, labels, topology, values, init_val:int=100):
    self.init_state = nx.Graph()
    for l, v in zip(labels, values):
      self.init_state.add_node(l, type=v, value=init_val)
    self.init_state.add_edges_from([[labels[t[0]], labels[t[1]]] for t in topology])

  def run_sim(self, n_step:int, f_update: Callable[[T.nGraph], T.nGraph]):
    state = self.init_state
    hist = [state]
    for _ in range(n_step):
      state = f_update(state)
      hist.append(state)
    
    return hist
  
  @classmethod
  def simulate(cls, id:int, model: Callable[[T.nGraph], T.nGraph], cli, mcl, logger, init_val:int=100):
      mcl.set(id, 1)
      store = Store()
      simcon = cls(**store.cval, init_val=init_val)
      mcl.set(id, 2)
      try:
          hist = simcon.run_sim(12*5, model)
      except Exception as exec:
          logger.error(exec)
          mcl.set(id, -1)
          return
      mcl.set(id, 3)
      cli.set(id, pickle.dumps([
          nx.get_node_attributes(h, 'value')
          for h in hist
      ]))
      mcl.set(id, 4)