from enum import Enum
import logging

from fastapi import BackgroundTasks, APIRouter, HTTPException
from google.cloud import firestore

from .service import types as T
from .service.visualizer import VizCon

logger = logging.getLogger("uvicorn")

router = APIRouter()
firestore_client = firestore.Client()

class Tags(Enum):
    viz = 'viz'

@router.get("/viz", tags=[Tags.viz])
def run_visualizer(id: str, bg_task: BackgroundTasks):
    ref = firestore_client.collection('results')
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")
    elif doc.get('status') != 4:
        raise HTTPException(status_code=404, detail="item_not_finished")


    ref_viz = firestore_client.collection('vizimg')
    doc_viz = ref_viz.document(id)

    bg_task.add_task(VizCon.visualize, id, ref, ref_viz, logger)

    doc_viz.set({
        "id": id,
        "status": 0,
        "url": '',
    })

    return {"url": f"https://storage.googleapis.com/instant-sim-viz/{id}.png"}