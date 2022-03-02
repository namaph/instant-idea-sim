from typing import Dict


def get_neighbor(graph, label) -> Dict[str, float]:
    res: Dict[str, float] = {}
    for i in graph[label]:
        t, v = graph.nodes[i].values()
        if t not in res.keys():
            res[t] = v
        else:
            res[t] += v
    return res
