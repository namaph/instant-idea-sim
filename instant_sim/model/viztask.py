from typing import List

from google.cloud.firestore_v1.transforms import Sentinel
from pydantic import BaseModel


class VizResult(BaseModel):
    id: str
    timestamp: Sentinel
    status: int
    step: int
    url: str

    class Config:
        arbitrary_types_allowed = True


class VizTask(BaseModel):
    simid: str
    vizresult: List[VizResult]
