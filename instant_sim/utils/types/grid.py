from typing import Any, Dict, Iterable, List, Tuple, Union

import numpy as np
import numpy.typing as npt
import pydantic import PositiveInt

from .simobj import SimObj

coord = Iterable[PositiveInt, PositiveInt]
grid = npt.NDArray[np.float_]


class Grid(SimObj):
    labels: List[str]
    attr: Dict[str, grid]
    pos: List[Tuple[coord, coord]]

    cache: List[str, Any]

    def __init__(
        self,
        labels: List[str],
        pos: List[Tuple[coord, coord]],
        shape: Tuple[PositiveInt, PositiveInt],
        **attr: Dict[str, List[Any]]
    ):
        assert len(labels) == len(pos)
        self.labels = labels
        self.pos = pos
        self.cache = {
            "label_index": {k: v for k, v in zip(labels, range(len(labels)))}
        }

        self.attr = {}
        for k, v in attr.items():
            temp = np.zeros(shape, dtype=np.float_)
            for p, val in zip(pos, v):
                temp[p] = val
            self.attr[k] = temp

    def __getitem__(self, key: Union[str, coord, List[str], List[coord]]) -> List[Dict[str, Any]]:
        temp = [key] if not isinstance(key, str) and isinstance(key[0], int) else key
        if isinstance(temp[0], str):
            return [{k: v[self.cache['label_index']][i] for k, v in self.attr.items()} for i in temp]
        else:
            return [{k: v[i] for k, v in self.attr.items()} for i in temp]
    
    def get_neighbor(self, key: Union[coord, List[coord]]) -> List[np.NDArray[np.float_]]:
        temp = [key] if not isinstance(key, str) and isinstance(key[0], int) else key
        ret = []
        for i in temp:
            top = np.asarray(
                [i+(-1,-1), i+(-1, 0), i+(-1, 1)],
                [i+( 0,-1), i+( 0, 0), i+( 0, 1)],
                [i+( 1,-1), i+( 1, 0), i+( 1, 1)]
            )
            ret.append({k: v[top] for k, v in self.attr.items()})
        return ret