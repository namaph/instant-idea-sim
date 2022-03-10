import io
import logging
from typing import Any, Optional, cast

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns
from google.cloud import storage
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.storage import Blob
from pydantic import PositiveInt

from instant_sim.utils.types import Graph, Grid, SimData, SimDataList

client_storage = storage.Client()
bucket = client_storage.get_bucket("instant-sim-viz")


class VizCon:
    content: SimData
    dtype: SimDataList
    logger: logging.Logger

    def __init__(self, content: SimData, logger: Optional[logging.Logger] = None):
        self.content = content
        self.logger = logging.getLogger("uvicorn") if logger is None else logger
        if isinstance(content, Grid):
            self.dtype = SimDataList.Grid
        elif isinstance(content, Graph):
            self.dtype = SimDataList.Graph
        else:
            raise TypeError(f"Class: {type(content)} doesn't match to SimData: Grid/Graph")

    def plot(self, fname: Any, attr: str) -> None:
        if self.dtype == SimDataList.Graph:
            cont = cast(Graph, self.content)
            row, col = np.where(cont.topology == 1)
            edges = zip(row.tolist(), col.tolist())
            gr = nx.Graph()
            gr.add_edges_from(edges)
            f, a = plt.subplots(figsize=(10, 10))
            nx.draw(
                gr,
                node_size=500,
                labels=cont.attr[attr],
                with_labels=True,
                font_size=10,
                font_color="w",
                node_color=col,
                ax=a,
            )
            f.savefig(fname)
        elif self.dtype == SimDataList.Grid:
            content = cast(Grid, self.content)
            target = content.attr[attr]
            f, a = plt.subplots(figsize=(10, 10))
            sns.heatmap(target, ax=a, cbar=False)
            f.savefig(fname)
        else:
            RuntimeError(f"Invalid dtype, expects SimData, got: {self.dtype}")

    @classmethod
    def visualize(
        cls, id: str, sdoc: DocumentReference, vdoc: DocumentReference, step: PositiveInt, attr: str
    ) -> None:
        target: SimData = sdoc.get().get("result")[step]
        vizcon = cls(target)
        try:
            bio = io.BytesIO()
            vizcon.plot(bio, attr)
        except Exception as excp:
            vizcon.logger.exception(excp)
            return
        fname = f"{id}_{step}_{type}.png"
        blob = Blob(fname, bucket)
        blob.upload_from_string(data=bio.getvalue(), content_type="image/png")
        vizcon.logger.debug(f"Done viz: {id}")
