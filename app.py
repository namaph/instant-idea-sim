from asyncio.log import logger
import datetime
import logging
import os
import pickle
import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException
import networkx as nx
import redis

from mylib import const as C
from mylib.datastore import Store
from mylib.simulator import SimCon
from mylib import util as U

if "LOCAL" not in os.environ:
    logging.debug(f'LOAD google debugger')
    try:
        import googleclouddebugger
        import googlecloudprofiler
        googleclouddebugger.enable(breakpoint_enable_canary=True)
        googlecloudprofiler.start(
            service='python-cloud-debug',
            service_version='1.0.1',
            # 0-error, 1-warning, 2-info, 3-debug
            verbose=3,
        )
    except (ValueError, NotImplementedError) as exc:
        logging.debug(exc)

app = FastAPI()

redis_host = os.environ.get('REDISHOST', 'localhost')
redis_port = int(os.environ.get('REDISPORT', 6379))
redis_pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    db=0
)
meta_pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    db=1
)

def _conn(pool):
    def conn():
        r = redis.StrictRedis(connection_pool=pool)
        try:
            r.ping()
        except redis.exceptions.ConnectionError as exc:
            logging.debug("No Connection Error")
            logging.debug(exc)
            r = None
        return r
    return conn

conn = _conn(redis_pool)
mcon = _conn(meta_pool)


@app.get("/")
def read_root():
    return {"message": "Hello This is Namaph Simulator"}

def simulate(id:int, model_name: C.SimName):
    cli = conn()
    mcl = mcon()

    if cli is None or mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")

    mcl.set(id, 1)
    store = Store()
    simcon = SimCon(**store.cval)
    mcl.set(id, 2)
    try:
        hist = simcon.run_sim(12*5, C.SimFunc.__dict__[model_name.name])
    except Exception as exec:
        logging.error(exec)
        mcl.set(id, -1)
    mcl.set(id, 3)
    cli.set(id, pickle.dumps([
        nx.get_node_attributes(h, 'value')
        for h in hist
    ]))
    mcl.set(id, 4)
    logging.debug(f"Done: {id} (model: {model_name})")

@app.get("/run/{model_name}")
async def run_simulator(model_name: C.SimName, bg_task: BackgroundTasks):
    id = str(uuid.uuid4())
    mcl = mcon()
    if mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")
    
    mcl.set(id, 0)
    mcl.set(f"{id}:timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    mcl.set(f"{id}:model_name", model_name)

    bg_task.add_task(simulate, id, model_name)
    return {
        "model_name": model_name,
        "id": id,
        "message": f"check the result here: /result/{id}"
    }

msg = {
    -1: 'error',
    0: 'recieved',
    1: 'provisioning',
    2: 'running',
    3: 'postproc',
    4: 'done'
}
@app.get("/result/{id}")
def check_result(id: str):
    mcl = mcon()
    if mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")

    if not mcl.exists(id):
        raise HTTPException(status_code=404, detail="item_not_found")
    
    st = int(mcl.get(id))
    t = str(mcl.get(f"{id}:model_name"))
    ret = {'status': msg[st], 'model_name': t}

    if st == 4:
        cli = conn()
        ret['hist'] = pickle.loads(cli.get(id))
    
    return ret

@app.get("/results")
def check_results():
    mcl = mcon()
    if mcl is None:
        raise HTTPException(status_code=500, detail="redis server not found")
    keys = mcl.keys("*:timestamp")
    vals = mcl.mget(keys)
    mname = mcl.mget([f'{k[:-10]}:model_name' for k in keys])
    
    return {k[:-10]: {"status": v, "model_name": m} for k, v, m in zip(keys, vals, mname)}

@app.delete("/result/{id}")
def check_result(id: str):
    mcl = mcon()
    cli = conn()

    if mcl is None or cli is None:
        raise HTTPException(status_code=500, detail="redis server not found")
    
    if not mcl.exists(id):
        raise HTTPException(status_code=404, detail="item_not_found")
    mcl.delete(*mcl.keys(f"{id}*"))
    cli.delete(id)