from typing import Callable, Dict, Union

import networkx as nx

from . import types as T
from .datastore import Store


class SimCon:
    init_state: T.nGraph

    def __init__(self, labels, topology, values, init_val: Union[int, Dict[str, int]] = 100):
        self.init_state = nx.Graph()
        for label, value in zip(labels, values):
            if isinstance(init_val, int):
                self.init_state.add_node(label, type=value, value=init_val)
            else:
                self.init_state.add_node(label, type=value, value=init_val[label])
        self.init_state.add_edges_from([[labels[t[0]], labels[t[1]]] for t in topology])

    def run_sim(self, n_step: int, f_update: Callable[[T.nGraph], T.nGraph]):
        state = self.init_state
        hist = [state]
        for _ in range(n_step):
            state = f_update(state)
            hist.append(state)

        return hist

    @classmethod
    def simulate(cls, id: str, model: Callable[[T.nGraph], T.nGraph], ref, logger, init_val: int = 100):
        doc = ref.document(id)
        doc.update({"status": 1})
        store = Store()
        simcon = cls(**store.cval, init_val=init_val)
        doc.update({"status": 2})
        try:
            hist = simcon.run_sim(12 * 5, model)
        except Exception as exec:
            logger.error(exec)
            doc.update({"status": -1})
            return
        doc.update({"status": 3})
        doc.update({"hist": [nx.get_node_attributes(h, "value") for h in hist]})
        doc.update({"status": 4})
