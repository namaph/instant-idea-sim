from typing import List

from google.cloud.firestore_v1.transforms import Sentinel
from pydantic import BaseModel, Field, Json


class SimTask(BaseModel):
    timestamp: Sentinel = Field(..., description="recieved time")
    id: str = Field(..., description="task id")
    status: int = Field(..., description="current working stage")
    model_name: str = Field(..., description="name of running model")
    result: List[Json] = Field(..., description="simulation result")

    class Config:
        arbitrary_types_allowed = True
