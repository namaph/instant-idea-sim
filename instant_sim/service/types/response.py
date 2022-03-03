from typing import Any, Dict, List, Optional

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from pydantic import BaseModel, Field


class Home(BaseModel):
    detail: str = Field(..., description="Message from server")


class Run(BaseModel):
    id: str = Field(..., description="session id")
    model_name: str = Field(..., description="Name of running sim")


class Result(BaseModel):
    status: str = Field(..., description="Current working stage")
    model_name: Optional[str] = Field(..., description="Name of running sim")
    hist: Optional[List[Dict[str, Any]]] = Field(..., description="Result of sim, only returns when status is done")


class _Results(BaseModel):
    id: str = Field(..., description="session id")
    timestamp: Optional[DatetimeWithNanoseconds] = Field(..., description="Recieved time")
    status: Optional[str] = Field(..., description="Current working stage")
    model_name: Optional[str] = Field(..., description="Name of running sim")


Results = List[_Results]


class DelResult(BaseModel):
    detail: str = Field(..., description="Message from server")
