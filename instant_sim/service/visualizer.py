import io
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from google.cloud import firestore, storage
from google.cloud.storage import Blob

from . import types as T
from .datastore import Store
from .grid import Grid
from .simulator import SimCon

client_storage = storage.Client()
bucket = client_storage.get_bucket("instant-sim-viz")


class VizCon:
    graph: List[T.nGraph]

    def __init__(self, graph):
        self.graph = [g for g in graph]

    def plot_graph(self, fname="./graph.png", step=-1):
        info = nx.get_node_attributes(self.graph[step], "type")
        val = nx.get_node_attributes(self.graph[step], "value")
        labels = {k: f"{k}:{val[k]}" for k, v in info.items()}
        cmap = ["green", "red", "blue"]
        col = [cmap[v] for k, v in info.items()]
        f, a = plt.subplots(figsize=(10, 10))
        nx.draw(
            self.graph[step],
            with_labels=True,
            labels=labels,
            font_size=10,
            font_color="w",
            node_size=500,
            node_color=col,
            ax=a,
        )
        f.savefig(fname)

    def plot_grid(self, pos, cont, fname="./grid.png", step=-1):
        grid = Grid(pos)
        grid.set_attr(nx.get_node_attributes(self.graph[step], cont).values())
        f, a = plt.subplots(figsize=(10, 10))
        sns.heatmap(grid.grid, ax=a, cbar=False)
        f.savefig(fname)

    @classmethod
    def visualize(cls, id: str, cont, vdoc, pos, year, logger, type="graph"):
        vdoc.update({"status": 1})
        hist = cont.get("hist")
        store = Store()
        graph = [SimCon(**store.cval, init_val=hist[year]).init_state]
        vizcon = cls(graph)
        vdoc.update({"status": 2})
        bio = io.BytesIO()
        try:
            if type == "graph":
                vizcon.plot_graph(bio)
            elif type == "grid":
                vizcon.plot_grid(pos, "value", bio)
            else:
                logger.error("No Viz selected")
                vdoc.update({"status": -1})
                return
        except Exception as excp:
            logger.exception(excp)
            vdoc.update({"status": -1})
            return
        vdoc.update({"status": 3})
        fname = f"{id}_{year}_{type}.png"
        blob = Blob(fname, bucket)
        blob.upload_from_string(data=bio.getvalue(), content_type="image/png")
        vdoc.update({"url": firestore.ArrayUnion(["https://storage.googleapis.com/instant-sim-viz/" + fname])})
        vdoc.update({"status": 4})
        logger.debug(f"Done viz: {id}")
