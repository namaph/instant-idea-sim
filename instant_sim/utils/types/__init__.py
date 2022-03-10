from enum import Enum
from typing import Union

from .graph import Graph
from .grid import Grid


class SimDataList(Enum):
    Grid: str = "Grid"
    Graph: str = "Graph"


SimData = Union[Grid, Graph]

__all__ = ["Graph", "Grid", "SimData", "SimDataList"]
