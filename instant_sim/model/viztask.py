from typing import List

from pydantic import BaseModel


class VizResult(BaseModel):
    id: str
    status: int
    step: int
    url: str

    class Config:
        arbitrary_types_allowed = True


class VizTask(BaseModel):
    simid: str
    vizresult: List[VizResult]
