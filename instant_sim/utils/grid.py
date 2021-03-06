from typing import Any, Dict, List, Tuple

import numpy as np
from numpy.typing import NDArray


class Grid:
    grid: NDArray
    pos: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]

    def __init__(self, pos: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]):
        self.grid = np.zeros((512, 512))
        self.pos = pos

    def __getitem__(self, key: str) -> NDArray:
        (a, b), (c, d) = self.pos[key]
        return self.grid[a:b, c:d]

    def __setitem__(self, key: str, val: Any) -> None:
        (a, b), (c, d) = self.pos[key]
        self.grid[a:b, c:d] = val

    def set_attr(self, val: List[int]) -> None:
        for k, v in zip(self.pos.keys(), val):
            self[k] = v
