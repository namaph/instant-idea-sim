from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.cloud.firestore import Query
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.transforms import Sentinel

from instant_sim import consensus_topic as C
from instant_sim import model, schema
from instant_sim.api import deps
from instant_sim.core.config import settings
from instant_sim.utils.simulator import SimCon

router = APIRouter()


@router.get("/run/{model_name}", response_model=schema.SimTaskCreate)
async def create_simtask(
    model_name: C.SimName,
    bg_task: BackgroundTasks,
    id: str = Depends(deps.get_uuid),
    client: Client = Depends(deps.get_firestore),
    time: Sentinel = Depends(deps.get_servertime),
) -> Any:
    doc = client.collection().document(id)

    doc.set(model.SimTask(id=id, timestamp=time, status=0, model_name=model_name, result=[]).dict())

    bg_task.add_task(SimCon.simulate, C.SimFunc.__dict__[model_name], doc)

    return schema.SimTaskCreate(
        id=id,
        model_name=model_name,
    )


@router.get("/result/{id}", response_model=schema.SimTask)
def get_sim_result(id: str, client: Client = Depends(deps.get_firestore)) -> Any:
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}

    cont = client.collection(settings.FIRESTORE_ROUTING.simulation_result).document(id).get()

    if not cont.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return schema.SimTask(
        id=cont.get("id"),
        model_name=cont.get("model_name"),
        timestamp=cont.get("timestamp"),
        status=msg[cont.get("status")],
        result=cont.get("result"),
    )


@router.get("/results", response_model=List[schema.SimTaskOverview])
def get_all_sim_results(client: Client = Depends(deps.get_firestore)) -> Any:
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}
    ref = client.collection(settings.FIRESTORE_ROUTING.simulation_result)

    query = ref.order_by("timestamp", direction=Query.DESCENDING)
    content = query.get()
    return [
        schema.SimTaskOverview(
            id=cont.get("id"),
            model_name=cont.get("model_name"),
            timestamp=cont.get("timestamp"),
            status=msg[cont.get("status")],
        )
        for cont in content
    ]


@router.delete("/result/{id}", response_model=schema.Msg)
def del_result(id: str, client: Client = Depends(deps.get_firestore)) -> Any:
    doc = client.collection(settings.FIRESTORE_ROUTING.simulation_result).document(id)

    if not doc.get().exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    doc.delete()
    return {"msg": "Success"}
