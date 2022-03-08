from typing import Dict

from networkx.classes.graph import Graph


def get_neighbor(graph: Graph, label: str) -> Dict[int, float]:
    res: Dict[int, float] = {}
    for i in graph[label]:
        t, v = graph.nodes[i].values()
        if t not in res.keys():
            res[t] = v
        else:
            res[t] += v
    return res
