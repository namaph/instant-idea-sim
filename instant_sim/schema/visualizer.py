from typing import List

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from pydantic import BaseModel, parse_object_as


class VizBase(BaseModel):
    simid: str


class VizTaskCreate(VizBase):
    id: str
    step: int
    url: str


class VizResult(BaseModel):
    id: str
    timestamp: DatetimeWithNanoseconds
    status: int
    step: int
    url: str


class VizTask(VizBase):
    vizresult: List[VizResult]

    def __init__(self, **data):
        res = parse_object_as(List[VizResult], data["vizresult"])
        super().__init__(simid=data["simid"], vizresult=res)
