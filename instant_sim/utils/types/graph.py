from typing import Any, Dict, List, Tuple, Union
from pydantic import PositiveInt

import numpy as np
import numpy.typing as npt

from .simobj import SimObj


class Graph(SimObj):
    labels: List[str]
    topology: npt.NDArray[np.int8]
    attr: Dict[str, List[Any]]
    attr_by_element: List[Dict[str, Any]]

    cache: List[str, Any]

    def __init__(
        self,
        labels: List[str],
        topology: List[Tuple[PositiveInt, PositiveInt]],
        **attr: Dict[str, List[Any]]
    ):
        assert max(sum(topology, ())) == len(labels), f"index number in topology indicates out of index, got: {max(sum(topology, ()))}"

        self.labels = labels
        self.topology = np.zeros((len(labels), len(labels)), dtype=np.int8)
        self.attr = attr.copy()
        self.attr_by_element = []

        for t in topology:
            self.topology[t] = 1
            self.topology[t[-1]] = 1

        for i in range(len(labels)):
            cont = {}
            for k, v in attr.items():
                cont[k] = v[i]
            self.attr_by_element.append(cont)
        
        self.cache['label_index'] = {k: i for i, k in enumerate(labels)}
    
    def __getitem__(self, key: Union[PositiveInt, str, List[PositiveInt], List[str]]) -> List[Dict[str, Any]]:
        temp = [key] if isinstance(key, (PositiveInt, str)) else key

        if len(key) == 0:
            return []
        
        if isinstance(temp[0], PositiveInt):
            return [self.attr_by_element[i] for i in temp]
        else:
            return [self.attr_by_element[self.cache['label_index'][i]] for i in temp]
    
    def get_neighbor(self, key: Union[PositiveInt, str, List[PositiveInt], List[str]]) -> List[PositiveInt]:
        temp = [key] if isinstance(key, (PositiveInt, str)) else key

        if len(key) == 0:
            return []
        
        index = np.arange(self.topology.shape[0])
        if isinstance(temp[0], PositiveInt):
            return [index[self.topology[i, :]] for i in temp]
        else:
            return [index[self.topology[self.cache['label_index'][i], :]] for i in temp]