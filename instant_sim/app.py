import datetime
import logging
import os
import pickle
import uuid

import const as C
from fastapi import BackgroundTasks, FastAPI, HTTPException
from service import types as T
from service import util as U
from service.simulator import SimCon

logger = logging.getLogger("uvicorn")

if "LOCAL" not in os.environ:
    logger.debug("LOAD google debugger")
    try:
        import googleclouddebugger
        import googlecloudprofiler

        googleclouddebugger.enable(breakpoint_enable_canary=True)
        googlecloudprofiler.start(
            service="python-cloud-debug",
            service_version="1.0.1",
            # 0-error, 1-warning, 2-info, 3-debug
            verbose=3,
        )
    except (ValueError, NotImplementedError) as exc:
        logger.debug(exc)

app = FastAPI()

redis_host = os.environ.get("REDISHOST", "localhost")
redis_port = int(os.environ.get("REDISPORT", 6379))

redis_pool = U.get_conn_pool(redis_host, redis_port, 0)
meta_pool = U.get_conn_pool(redis_host, redis_port, 1)

conn = U.get_conn(redis_pool)
mcon = U.get_conn(meta_pool)


@app.get("/", response_model=T.resp.Home)
def read_root():
    return T.resp.Home(detail="Hello This is Namaph Simulator")


@app.get("/run/{model_name}", response_model=T.resp.Run)
async def run_simulator(model_name: C.SimName, bg_task: BackgroundTasks):
    id = str(uuid.uuid4())
    cli, mcl = conn(), mcon()
    if cli is None or mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")

    mcl.set(id, 0)
    mcl.set(f"{id}:timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    mcl.set(f"{id}:model_name", model_name)

    bg_task.add_task(SimCon.simulate, id, C.SimFunc.__dict__[model_name], cli, mcl, logger)

    return T.resp.Run(
        model_name=model_name,
        id=id,
    )


@app.get("/result/{id}", response_model=T.resp.Result)
def check_result(id: str):
    msg = {-1: "error", 0: "recieved", 1: "provisioning", 2: "running", 3: "postproc", 4: "done"}
    cli, mcl = conn(), mcon()
    if cli is None or mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")

    if not mcl.exists(id):
        raise HTTPException(status_code=404, detail="item_not_found")

    st = int(mcl.get(id))
    t = mcl.get(f"{id}:model_name").decode("ascii")
    return T.resp.Result(status=msg[st], model_name=str(t), hist=pickle.loads(cli.get(id)) if st == 4 else None)


@app.get("/results", response_model=T.resp.Results)
def get_results():
    cli, mcl = conn(), mcon()
    if cli is None or mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")
    keys = [k.decode("ascii")[:-10] for k in mcl.keys("*:timestamp")]
    status = mcl.mget(keys)
    timestamp = mcl.mget([f"{k}:timestamp" for k in keys])
    mname = mcl.mget([f"{k}:model_name" for k in keys])

    return [
        T.resp._Results(id=k, timestamp=t.decode("ascii"), status=int(s), model_name=m.decode("ascii"))
        for k, s, t, m in zip(keys, status, timestamp, mname)
    ]


@app.delete("/result/{id}", response_model=T.resp.DelResult)
def del_result(id: str):
    mcl = mcon()
    cli = conn()

    if mcl is None or cli is None:
        raise HTTPException(status_code=500, detail="redis server not found")

    if not mcl.exists(id):
        raise HTTPException(status_code=404, detail="item_not_found")
    mcl.delete(*mcl.keys(f"{id}*"))
    cli.delete(id)
    return T.resp.DelResult(detail="Success")
