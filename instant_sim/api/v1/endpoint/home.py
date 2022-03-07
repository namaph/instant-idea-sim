from typing import Any

from fastapi import APIRouter

from instant_sim import schema

router = APIRouter()


@router.get("/", response_model=schema.Msg)
def read_root() -> Any:
    return {"msg": "Hello This is Namaph Instant Simulator"}
