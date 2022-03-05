import logging
import os
import uuid

import const as C
from fastapi import BackgroundTasks, FastAPI, HTTPException
from google.cloud import firestore
from service import types as T
from service.simulator import SimCon

logger = logging.getLogger("uvicorn")

# if "LOCAL" not in os.environ:
#     logger.debug("LOAD google debugger")
#     try:
#         import googleclouddebugger
#         import googlecloudprofiler

#         googleclouddebugger.enable(breakpoint_enable_canary=True)
#         googlecloudprofiler.start(
#             service="python-cloud-debug",
#             service_version="1.0.1",
#             # 0-error, 1-warning, 2-info, 3-debug
#             verbose=3,
#         )
#     except (ValueError, NotImplementedError) as exc:
#         logger.debug(exc)

app = FastAPI()
firestore_client = firestore.Client()


@app.get("/", response_model=T.resp.Home)
def read_root():
    return T.resp.Home(detail="Hello This is Namaph Simulator")


@app.get("/run/{model_name}", response_model=T.resp.Run)
async def run_simulator(model_name: C.SimName, bg_task: BackgroundTasks):
    id = str(uuid.uuid4())
    ref = firestore_client.collection("results")

    ref.document(id).set({"timestamp": firestore.SERVER_TIMESTAMP, "status": 0, "model_name": model_name, "hist": []})

    bg_task.add_task(SimCon.simulate, id, C.SimFunc.__dict__[model_name], ref, logger)

    return T.resp.Run(
        model_name=model_name,
        id=id,
    )


@app.get("/result/{id}", response_model=T.resp.Result)
def check_result(id: str):
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}

    ref = firestore_client.collection("results")
    doc = ref.document(id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    return T.resp.Result(status=msg[doc.get("status")], model_name=doc.get("model_name"), hist=doc.get("hist"))


@app.get("/results", response_model=T.resp.Results)
def get_results():
    ref = firestore_client.collection("results")

    query = ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
    content = query.get()
    return [
        T.resp._Results(id=c.id, timestamp=c.get("timestamp"), status=c.get("status"), model_name=c.get("model_name"))
        for c in content
    ]


@app.delete("/result/{id}", response_model=T.resp.DelResult)
def del_result(id: str):
    ref = firestore_client.collection("results")
    docs = ref.document(id)

    if not docs.get().exists:
        raise HTTPException(status_code=404, detail="item_not_found")

    docs.delete()
    return T.resp.DelResult(detail="Success")
