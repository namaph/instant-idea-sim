import io
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns

from google.cloud import storage
from google.cloud.storage import Blob

from . import types as T
from .grid import Grid
from .simulator import SimCon
from .datastore import Store

client_storage = storage.Client()
bucket = client_storage.get_bucket('instant-sim-viz')

class VizCon:
    graph: List[T.nGraph]

    def __init__(self, graph):
        self.graph = [g for g in graph]

    def plot_graph(self, fname="./graph.png", pos=-1):
        info = nx.get_node_attributes(self.graph[pos], "type")
        val = nx.get_node_attributes(self.graph[pos], "value")
        labels = {k: f"{k}:{val[k]}" for k, v in info.items()}
        cmap = {"1": "green", "2": "red", "3": "blue"}
        col = [cmap[v] for k, v in info.items()]
        nx.draw(self.graph[pos], with_labels=True, labels=labels, font_size=10, font_color="w", node_size=500, node_color=col)
        plt.savefig(fname)


    def plot_grid(self, pos, cont, fname="./grid.png"):
        grid = Grid(pos)
        grid.set_attr(nx.get_node_attributes(self.graph[pos], cont).values())
        f, a = plt.subplots(figsize=(10, 10))
        sns.heatmap(grid.grid, ax=a, cbar=False)
        f.savefig(fname)

    @classmethod
    def visualize(cls, id:str, ref, vref, logger, type='graph'):
        doc = vref.document(id)
        doc.update({'status': 1})
        hist = ref.document(id).get().get('hist')
        store = Store()
        graph = [SimCon(**store.cval, init_val=hist[-1]).init_state]
        vizcon = cls(graph)
        doc.update({'status': 2})
        bio = io.BytesIO()
        vizcon.plot_graph(bio)
        doc.update({'status': 3})
        blob = Blob(f'{id}.png', bucket)
        blob.upload_from_string(data=bio.getvalue(), content_type="image/png")
        doc.update({"url": f"https://storage.googleapis.com/instant-sim-viz/{id}.png"})
        doc.update({'status': 4})
        logger.debug('Done')