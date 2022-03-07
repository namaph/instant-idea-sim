from typing import List

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from pydantic import BaseModel, Json


class SimBase(BaseModel):
    id: str
    model_name: str


class SimTaskCreate(SimBase):
    pass


class SimTask(SimBase):
    timestamp: DatetimeWithNanoseconds
    status: str
    result: List[Json]
