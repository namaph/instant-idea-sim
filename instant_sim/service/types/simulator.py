from typing import NewType

import networkx as nx

nGraph = NewType("nGraph", nx.classes.graph.Graph)  # type: ignore
