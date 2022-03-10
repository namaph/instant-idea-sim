import logging
from typing import Callable, List, Optional, Tuple

from google.cloud.firestore_v1.document import DocumentReference
from pydantic import PositiveInt

from instant_sim import consensus_topic as C
from instant_sim.utils.datastore import Store
from instant_sim.utils.types import Graph, Grid, SimData, SimDataList


class SimCon:
    state: SimData
    logger: logging.Logger

    def __init__(
        self,
        labels: List[str],
        topology: List[Tuple[int, int]],
        values: List[int],
        dtype: SimDataList,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logging.getLogger("uvicorn") if logger is None else logger
        self.dtype = dtype
        if dtype == SimDataList.Graph:
            self.state = Graph(labels, topology, land_type=values, value=C.init_val)  # type: ignore
        if dtype == SimDataList.Grid:
            self.state = Grid(labels, C.pos, C.gridshape, land_type=values, value=C.init_val)  # type: ignore

    def run_sim(self, n_step: PositiveInt, f_update: Callable[[SimData], SimData]) -> List[SimData]:
        state = self.state
        hist = [state]
        for _ in range(n_step):
            state = f_update(state)
            hist.append(state)

        return hist

    @classmethod
    def simulate(cls, model: Callable[[SimData], SimData], doc: DocumentReference, dtype: SimDataList) -> None:
        doc.update({"status": 1})
        store = Store().cont
        simcon = cls(store.labels, store.topology, store.values, dtype)
        doc.update({"status": 2})
        try:
            result = simcon.run_sim(C.period, model)
        except Exception as exec:
            simcon.logger.exception(exec)
            doc.update({"status": -1})
            return
        doc.update({"status": 3})
        doc.update({"result": [r.dict() for r in result]})
        doc.update({"status": 4})
