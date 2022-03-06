import logging
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, HTTPException
from google.cloud import firestore

from . import const as C
from .service import types as T
from .service.visualizer import VizCon

logger = logging.getLogger("uvicorn")

router = APIRouter()
firestore_client = firestore.Client()


class Tags(Enum):
    viz = "viz"


@router.get("/viz/{viz_name}", response_model=T.resp.Visualize, tags=[Tags.viz])
def run_visualizer(id: str, viz_name: C.VizName, bg_task: BackgroundTasks, step: int = -1):
    year = step
    ref = firestore_client.collection("results")
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")
    elif doc.get("status") != 4:
        raise HTTPException(status_code=404, detail="item_not_finished")

    ref_viz = firestore_client.collection("vizimg")
    doc_viz = ref_viz.document(id)

    pos = C.pos
    bg_task.add_task(VizCon.visualize, id, ref, ref_viz, pos, year, logger, viz_name.value)

    if doc_viz.get().exists:
        doc_viz.update(
            {
                "status": 0,
                "step": firestore.ArrayUnion([year]),
            }
        )
    else:
        doc_viz.set(
            {
                "id": id,
                "status": 0,
                "step": [year],
                "url": [],
            }
        )

    return T.resp.Visualize(
        id=id,
        status=0,
        step=year,
        url=f"https://storage.googleapis.com/instant-sim-viz/{id}_<step>.png",
    )


@router.get("/vizresult/{id}", response_model=T.resp._Visualize, tags=[Tags.viz])
def check_result(id: str):
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}

    ref = firestore_client.collection("vizimg")
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return T.resp.Visualize(id=id, status=msg[doc.get("status")], url=doc.get("url"), step=doc.get("step"))
