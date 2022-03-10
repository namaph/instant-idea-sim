import abc
from typing import Any, Dict, List

from pydantic import BaseModel


class SimObj(BaseModel, abc.ABC):
    @abc.abstractmethod
    def __getitem__(self, key: Any) -> List[Dict[str, Any]]:
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
    def get_neighbor(self, key: Any) -> List[Any]:
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
