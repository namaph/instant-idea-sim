from enum import Enum
import logging

from fastapi import FastAPI

from . import app_model
from . import app_viz

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

app = FastAPI()
app.include_router(app_model.router)
app.include_router(app_viz.router)

@app.get("/", response_model=T.resp.Home)
def read_root():
    return T.resp.Home(detail="Hello This is Namaph Simulator")