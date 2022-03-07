from typing import Dict, List, Tuple

from pydantic import BaseModel


class MetaCityioResp(BaseModel):
    hash: str
    hashes: Dict[str, str]
    id: str
    timestamp: str


class CityioResp(BaseModel):
    labels: List[str]
    meta: MetaCityioResp
    topology: List[Tuple[int, int]]
    values: List[int]

    def __init__(self, **data) -> None:
        meta = MetaCityioResp(**data["meta"])
        super().__init__(labels=data["labels"], meta=meta, topology=data["topology"], values=data["values"])
