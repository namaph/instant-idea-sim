import logging
import uuid
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, HTTPException
from google.cloud import firestore

from . import const as C
from .service import types as T
from .service.simulator import SimCon

logger = logging.getLogger("uvicorn")

router = APIRouter()
firestore_client = firestore.Client()


class Tags(Enum):
    model = "model"


@router.get("/run/{model_name}", response_model=T.resp.Run, tags=[Tags.model])
async def run_simulator(model_name: C.SimName, bg_task: BackgroundTasks):
    id = str(uuid.uuid4())
    ref = firestore_client.collection("results")

    ref.document(id).set({"timestamp": firestore.SERVER_TIMESTAMP, "status": 0, "model_name": model_name, "hist": []})

    bg_task.add_task(SimCon.simulate, id, C.SimFunc.__dict__[model_name], ref, logger)

    return T.resp.Run(
        model_name=model_name,
        id=id,
    )


@router.get("/result/{id}", response_model=T.resp.Result, tags=[Tags.model])
def check_result(id: str):
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}

    ref = firestore_client.collection("results")
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return T.resp.Result(status=msg[doc.get("status")], model_name=doc.get("model_name"), hist=doc.get("hist"))


@router.get("/results", response_model=T.resp.Results, tags=[Tags.model])
def get_results():
    ref = firestore_client.collection("results")

    query = ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
    content = query.get()
    return [
        T.resp._Results(id=c.id, timestamp=c.get("timestamp"), status=c.get("status"), model_name=c.get("model_name"))
        for c in content
    ]


@router.delete("/result/{id}", response_model=T.resp.DelResult, tags=[Tags.model])
def del_result(id: str):
    ref = firestore_client.collection("results")
    docs = ref.document(id)

    if not docs.get().exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    docs.delete()
    return T.resp.DelResult(detail="Success")
