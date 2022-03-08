from typing import Any, List

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from pydantic import BaseModel


class SimBase(BaseModel):
    id: str
    model_name: str


class SimTaskCreate(SimBase):
    pass


class SimTaskOverview(SimBase):
    timestamp: DatetimeWithNanoseconds
    status: str


class SimTask(SimBase):
    timestamp: DatetimeWithNanoseconds
    status: str
    result: List[Any]
