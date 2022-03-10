from typing import Any, Dict, List, Tuple, Union, cast

import numpy as np
import numpy.typing as npt
from pydantic import Field, PositiveInt

from .simobj import SimObj

coord = Tuple[PositiveInt, PositiveInt]
grid = npt.NDArray[np.float_]


class Grid(SimObj):
    labels: List[str]
    attr: Dict[str, grid]
    pos: List[Tuple[coord, coord]]
    shape: Tuple[PositiveInt, PositiveInt]

    cache: Dict[str, Any]

    def __init__(
        self,
        labels: List[str],
        pos: List[Tuple[coord, coord]],
        shape: Tuple[PositiveInt, PositiveInt],
        *,
        attr: Dict[str, List[Any]],
    ):
        assert len(labels) == len(pos)
        self.labels = labels
        self.pos = pos
        self.cache = {"label_index": {k: v for k, v in zip(labels, range(len(labels)))}}

        self.attr = {}
        self.shape = shape
        for k, v in attr.items():
            temp = np.zeros(shape, dtype=np.float_)
            for p, val in zip(pos, v):
                temp[p] = val
            self.attr[k] = temp

    def __getitem__(self, key: Union[str, coord, List[str], List[coord]]) -> List[Dict[str, Any]]:
        temp = [key] if not isinstance(key, list) else key

        if isinstance(temp[0], str):
            return [{k: v[self.cache["label_index"]][cast(str, i)] for k, v in self.attr.items()} for i in temp]
        else:
            return [{k: v[cast(int, i)] for k, v in self.attr.items()} for i in temp]

    def get_neighbor(self, key: Union[coord, List[coord]]) -> List[grid]:
        temp = [key] if not isinstance(key, list) else key
        ret = []
        for t in temp:
            i = np.asarray(t)
            top = np.asarray(
                [
                    [i + (-1, -1), i + (-1, 0), i + (-1, 1)],
                    [i + (0, -1), i + (0, 0), i + (0, 1)],
                    [i + (1, -1), i + (1, 0), i + (1, 1)],
                ]
            )
            ret.append(top)
        return ret

    def get_neighbor_grid(
        self, coef: List[float] = Field([1, 1, 1, 1, 1, 1, 1, 1, 1], min_length=9, max_length=9)
    ) -> Dict[str, grid]:

        neighbor: Dict[str, grid] = {}
        if f"neighbor{coef}" not in self.cache.keys():
            for k, v in self.attr.items():
                buffer: grid = np.zeros((self.shape[0] + 2, self.shape[1] + 2), dtype=np.float_)
                buffer[:-2, :-2] += v * coef[0]
                buffer[1:-1, :-2] += v * coef[1]
                buffer[2:, :-2] += v * coef[2]
                buffer[:-2, 1:-1] += v * coef[3]
                buffer[1:-1, 1:-1] += v * coef[4]
                buffer[2:, 1:-1] += v * coef[5]
                buffer[:-2, 2:] += v * coef[6]
                buffer[1:-1, 2:] += v * coef[7]
                buffer[2:, 2:] += v * coef[8]
                neighbor["k"] = buffer
            self.cache[f"neighbor{coef}"] = neighbor
        else:
            neighbor = self.cache[f"neighbor{coef}"]

        return neighbor
