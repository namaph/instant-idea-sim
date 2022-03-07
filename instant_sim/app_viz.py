from fastapi import APIRouter, BackgroundTasks, HTTPException
from google.cloud import firestore

from . import const as C
from .service import types as T
from .service.visualizer import VizCon

router = APIRouter()
firestore_client = firestore.Client()


@router.get("/viz/{viz_name}", response_model=T.resp.Visualize)
def run_visualizer(id: str, viz_name: C.VizName, bg_task: BackgroundTasks, step: int = -1):
    cont = firestore_client.collection("results").document(id).get()

    if not cont.exists:
        raise HTTPException(status_code=404, detail="item_not_found")
    elif cont.get("status") != 4:
        raise HTTPException(status_code=404, detail="item_not_finished")

    length = len(cont.get("hist")) - 1
    vstep = length if step == -1 else step
    vdoc = firestore_client.collection("vizimg").document(id)

    if vdoc.get().exists:
        vdoc.update(
            {
                "status": 0,
                "step": firestore.ArrayUnion([vstep]),
            }
        )
    else:
        vdoc.set(
            {
                "id": id,
                "status": 0,
                "step": [vstep],
                "url": [],
            }
        )

    bg_task.add_task(VizCon.visualize, id, cont, vdoc, C.pos, vstep, viz_name.value)
    fname = f"{id}_{vstep}_{viz_name.value}.png"

    return T.resp.Visualize(
        id=id,
        status=0,
        step=vstep,
        url=f"https://storage.googleapis.com/instant-sim-viz/{fname}",
    )


@router.get("/vizresult/{id}", response_model=T.resp.VizResult)
def check_result(id: str):
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}

    ref = firestore_client.collection("vizimg")
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return T.resp.VizResult(id=id, status=msg[doc.get("status")], url=doc.get("url"), step=doc.get("step"))
