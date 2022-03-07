from enum import Enum

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import app_model, app_viz
from .service import types as T

# import os
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


class Tags(Enum):
    model = "model"
    viz = "viz"


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


app.include_router(app_model.router, tags=[Tags.model])
app.include_router(app_viz.router, tags=[Tags.viz])


@app.get("/", response_model=T.resp.Home)
def read_root():
    return T.resp.Home(detail="Hello This is Namaph Simulator")
