import io
import logging
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from google.cloud import storage
from google.cloud.storage import Blob
from networkx.classes.graph import Graph

from .datastore import Store
from .grid import Grid
from .simulator import SimCon

client_storage = storage.Client()
bucket = client_storage.get_bucket("instant-sim-viz")


class VizCon:
    graph: List[Graph]
    logger: logging.Logger

    def __init__(self, graph: Graph):
        self.graph = [g for g in graph]
        self.logger = logging.getLogger("uvicorn")

    def plot_graph(self, fname: Any = "./graph.png", step: int = -1) -> None:
        info = nx.get_node_attributes(self.graph[step], "type")
        val = nx.get_node_attributes(self.graph[step], "value")
        labels = {k: f"{k}:{val[k]}" for k, v in info.items()}
        cmap = ["black", "green", "red", "blue"]
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

    def plot_grid(
        self,
        pos: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
        cont: Any,
        fname: Any = "./grid.png",
        step: int = -1,
    ) -> None:
        grid = Grid(pos)
        grid.set_attr(nx.get_node_attributes(self.graph[step], cont).values())
        f, a = plt.subplots(figsize=(10, 10))
        sns.heatmap(grid.grid, ax=a, cbar=False)
        f.savefig(fname)

    @classmethod
    def visualize(
        cls,
        id: str,
        cont: Any,
        pos: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]],
        step: int,
        type: str = "graph",
    ) -> None:
        hist = cont.get("result")
        store = Store().cont
        simcon = SimCon(store.labels, store.topology, store.values, init_val=hist[step])
        graph = [simcon.init_state]
        vizcon = cls(graph)
        bio = io.BytesIO()
        try:
            if type == "graph":
                vizcon.plot_graph(bio)
            elif type == "grid":
                vizcon.plot_grid(pos, "value", bio)
            else:
                vizcon.logger.error("No Viz selected")
                return
        except Exception as excp:
            vizcon.logger.exception(excp)
            return
        fname = f"{id}_{step}_{type}.png"
        blob = Blob(fname, bucket)
        blob.upload_from_string(data=bio.getvalue(), content_type="image/png")
        vizcon.logger.debug(f"Done viz: {id}")
