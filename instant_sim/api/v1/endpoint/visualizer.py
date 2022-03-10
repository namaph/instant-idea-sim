from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.cloud.firestore import ArrayUnion
from google.cloud.firestore_v1.client import Client

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
) -> Any:
    cont = client.collection(settings.FIRESTORE_ROUTING.simulation_result).document(simid).get()

    if not cont.exists:
        raise HTTPException(status_code=404, detail="item_not_found")
    elif cont.get("status") != 4:
        raise HTTPException(status_code=400, detail="item_not_finished")

    length = len(cont.get("result")) - 1
    st = length if step == -1 else step
    doc = client.collection(settings.FIRESTORE_ROUTING.visualization_result).document(simid)

    if not doc.get().exists:
        doc.set(model.VizTask(simid=simid, vizresult=[]).dict())

    fname = f"{id}_{st}_{viz_name.value}.png"

    doc.update(
        {
            "vizresult": ArrayUnion([model.VizResult(id=id, status=0, step=st, url=settings.GCS_ROOT + fname).dict()]),
        }
    )

    bg_task.add_task(VizCon.visualize, id, cont, C.pos, st, viz_name.value)

    return schema.VizTaskCreate(id=id, simid=simid, step=st, url=settings.GCS_ROOT + fname)


@router.get("/vizresult/{simid}", response_model=schema.VizTask)
def check_result(simid: str, client: Client = Depends(deps.get_firestore)) -> Any:
    doc = client.collection(settings.FIRESTORE_ROUTING.visualization_result).document(simid).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return schema.VizTask(simid=simid, vizresult=doc.get("vizresult"))
