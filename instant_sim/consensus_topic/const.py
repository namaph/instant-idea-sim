# Constant Value Config File
from enum import Enum
from typing import NewType

import networkx as nx

from . import util as U

# be ... begining of grid
# la ... end of grid (last)
# ud ... Buffer area of up and buttom
# ma ... Buffer area of left and right
# s1 ... Town section, A~I
# s2 ... Town section, J~R
# s3 ... Town section, S~U

be = 0
la = 512
ud = 56
ma = 16
s1 = (ud, ud + 125)
s2 = (s1[1] + 10, s1[1] + 200)
s3 = (s2[1] + 10, s2[1] + 75)

pos = {
    "A": ((be, ud), (be, la)),
    "B": ((ud, -ud), (-ma, la)),
    "C": ((-ud, la), (be, la)),
    "D": ((ud, -ud), (be, ma)),
    "E": ((s1[0], s1[1] - 25), (ma, ma + 160)),
    "F": ((s1[0] + 20, s1[1] - 40), (ma + 180, ma + 280)),
    "G": ((s1[0], s1[0] + 30), (ma + 300, ma + 440)),
    "H": ((s1[0] + 35, s1[0] + 55), (ma + 300, ma + 440)),
    "I": ((s1[0] + 60, s1[0] + 125), (ma + 300, ma + 440)),
    "J": ((s2[0], s2[0] + 50), (ma, ma + 70)),
    "K": ((s2[0] + 30, s2[0] + 70), (ma + 70, ma + 160)),
    "L": ((s2[0], s2[0] + 30), (ma + 140, ma + 210)),
    "M": ((s2[0], s2[0] + 60), (ma + 210, ma + 310)),
    "N": ((s2[0], s2[0] + 60), (ma + 310, ma + 440)),
    "O": ((s2[0] + 70, s2[1]), (ma + 0, ma + 100)),
    "P": ((s2[0] + 70, s2[1]), (ma + 130, ma + 250)),
    "Q": ((s2[0] + 70, s2[1]), (ma + 270, ma + 420)),
    "R": ((s2[0] + 70, s2[1]), (ma + 450, -ma)),
    "S": (s3, (ma, ma + 100)),
    "T": (s3, (ma + 130, ma + 250)),
    "U": (s3, (ma + 270, ma + 420)),
}

init_val = 100


class SimName(str, Enum):
    economics = "economics"
    biodiv = "biodiv"


class VizName(str, Enum):
    graph = "graph"
    grid = "grid"


class NodeType(int, Enum):
    primary_ind = 1
    secondary_ind = 2
    tertiary_ind = 3


class NodeAttr(str, Enum):
    type = "type"
    value = "value"


nGraph = NewType("nGraph", nx.classes.graph.Graph)  # type: ignore


def f_update(graph: nGraph) -> nGraph:
    for i in graph.nodes:
        _ = graph.nodes[i]["type"]
        _ = U.get_neighbor(graph, i)
    return graph


def Biodiv(graph: nGraph) -> nGraph:
    ret = graph.copy()
    for i in graph.nodes:
        t = graph.nodes[i]["type"]
        v = graph.nodes[i]["value"]
        if t != str(NodeType.primary_ind.value):
            continue
        nbr = U.get_neighbor(graph, i)
        print(nbr)
        nbr1 = (nbr["1"] / 100) if "1" in nbr.keys() else 0
        nbr2 = (nbr["2"] / 100) if "2" in nbr.keys() else 0
        est = v * 1.1 + 5 * (nbr1 - nbr2 - 1)
        ret.nodes[i]["value"] = est
    return ret


def Economics(graph: nGraph) -> nGraph:
    ret = graph.copy()

    val = nx.get_node_attributes(graph, "value")
    typ = nx.get_node_attributes(graph, "type")

    amnt = [0, 0, 0, 0]
    count = [0, 0, 0, 0]
    for k in val.keys():
        amnt[typ[k]] += val[k]
        count[typ[k]] += 1

    r1 = amnt[1] * 1.5
    r2 = (r1 / 2) / 5
    r3 = max((r1 / 5) / 2, (r2 / 3) / 2)
    res = [
        0, 
        (r1 - r2 * 5 - r3 * 2) / count[1] if count[1] != 0 else 0,
        r2 - r3 / count[2] if count[2] != 0 else 0,
        r3 / count[3] if count[3] != 0 else 0
    ]

    for i in graph.nodes:
        t = graph.nodes[i]["type"]

        nbr = U.get_neighbor(graph, i)
        nbr1 = (nbr[1] / 100) if "1" in nbr.keys() else 0
        est = 0.0

        if t != str(NodeType.primary_ind.value):
            est = res[1] * 10 + 20 * nbr1
        elif t != str(NodeType.secondary_ind.value):
            est = res[2] * 20 + 10 * nbr1
        elif t != str(NodeType.tertiary_ind.value):
            est = res[3] * 30

        ret.nodes[i]["value"] = est
    return ret


class SimFunc(Enum):
    economics = Economics
    biodiv = Biodiv
