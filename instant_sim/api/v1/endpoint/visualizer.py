from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.cloud.firestore import ArrayUnion
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.transforms import Sentinel

from instant_sim import consensus_topic as C
from instant_sim import model, schema
from instant_sim.api import deps
from instant_sim.core.config import settings
from instant_sim.utils.visualizer import VizCon

router = APIRouter()


@router.get("/viz/{viz_name}", response_model=schema.VizTaskCreate)
def create_viztask(
    simid: str,
    viz_name: C.VizName,
    bg_task: BackgroundTasks,
    step: int = -1,
    id: str = Depends(deps.get_uuid),
    client: Client = Depends(deps.get_firestore),
    time: Sentinel = Depends(deps.get_servertime),
) -> Any:
    cont = client.collection("results").document(simid).get()

    if not cont.exists:
        raise HTTPException(status_code=404, detail="item_not_found")
    elif cont.get("status") != 4:
        raise HTTPException(status_code=400, detail="item_not_finished")

    length = len(cont.get("hist")) - 1
    st = length if step == -1 else step
    doc = client.collection("viz_img").document(simid)

    if not doc.get().exists:
        doc.set(model.VizTask(simid=simid, vizresult=[]).dict())
    doc.update(
        {
            "vizresult": ArrayUnion([model.VizResult(id=id, timestamp=time, status=0, step=st, url="").dict()]),
        }
    )

    bg_task.add_task(VizCon.visualize, id, cont, doc, C.pos, st, viz_name.value)
    fname = f"{id}_{st}_{viz_name.value}.png"

    return schema.VizTaskCreate(id=id, simid=simid, step=st, url=settings.GCS_ROOT + fname)


@router.get("/vizresult/{id}", response_model=schema.VizTask)
def check_result(simid: str, client: Client = Depends(deps.get_firestore)) -> Any:
    doc = client.collection("viz_img").document(simid).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return schema.VizTask(simid=simid, vizresult=doc.get("vizresult"))
