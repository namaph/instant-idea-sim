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

app = FastAPI()
app.include_router(app_model.router)
app.include_router(app_viz.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

@app.get("/", response_model=T.resp.Home)
def read_root():
    return T.resp.Home(detail="Hello This is Namaph Simulator")
