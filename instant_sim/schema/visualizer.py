from typing import Any, Dict, List

from pydantic import BaseModel, parse_obj_as


class VizBase(BaseModel):
    simid: str


class VizTaskCreate(VizBase):
    id: str
    step: int
    url: str


class VizResult(BaseModel):
    id: str
    status: int
    step: int
    url: str


class VizTask(VizBase):
    vizresult: List[VizResult]

    def __init__(self, **data: Dict[str, Any]):
        res = parse_obj_as(List[VizResult], data["vizresult"])
        super().__init__(simid=data["simid"], vizresult=res)
