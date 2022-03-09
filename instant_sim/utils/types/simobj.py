import abc
from typing import Any, Dict, List, , TypeVar, Union
from pydantic import BaseModel

T = TypeVar('T')
U = TypeVar('U')

class SimObj(BaseModel, abc.ABC):
    labels: List[str]
    topology: npt.NDArray[np.int8]
    attr: Dict[str, List[Any]]
    attr_by_element: List[Dict[str, Any]]

    cache: List[str, Any]

    @abc.abstractmethod
    def __init__(
        self,
        labels: List[str],
        topology: List[Tuple[PositiveInt, PositiveInt]],
        init_val: List[int],
        **attr: Dict[str, List[Any]]
    ):
        pass

    @abc.abstractmethod
    def __getitem__(self, key: Union[T, List[T]]) -> List[Dict[str, Any]]:
        """
        Extract the attributes from key

        Arguments
        ---------
        key: Union[T, List[T]]
            target location
        
        Returns
        -------
        val: List[Dict[str, Any]]
            list of attr-name and attr-val pairs
        """
        pass
    
    @abc.abstractmethod
    def get_neighbor(self, key: Union[T, List[T]]) -> List[U]:
        """
        Get the topology from key

        Arguments
        ---------
        key: Union[T, List[T]] 
            target location
        
        Returns
        -------
        top: U
            list of topology
        """
        pass