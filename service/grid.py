from typing import Dict, List, Tuple

from numpy.typing import NDArray
import numpy as np

class Grid():
  grid: NDArray
  pos: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]

  def __init__(self, pos, size=512):
    self.grid = np.zeros((512, 512))
    self.pos = pos

  def __getitem__(self, key):
    (a, b), (c, d) = self.pos[key]
    return self.grid[a:b, c:d]
  
  def __setitem__(self, key, val):
    (a, b), (c, d) = self.pos[key]
    self.grid[a:b, c:d] = val
  
  def set_attr(self, val: List[int]):
    for k, v in zip(self.pos.keys(), val):
      self[k] = v