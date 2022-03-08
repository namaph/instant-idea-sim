import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from instant_sim.api.v1.api import api_router
from instant_sim.core.config import settings

logger = logging.getLogger(__name__)

if settings.USE_GCP_DEBUGGER:
    logger.debug("LOAD google debugger")
    try:
        import googleclouddebugger

        googleclouddebugger.enable(breakpoint_enable_canary=True)
    except (ValueError, NotImplementedError) as exc:
        logger.debug(exc)

if settings.USE_GCP_PROFILER:
    logger.debug("LOAD google profiler")
    try:
        import googlecloudprofiler

        googlecloudprofiler.start(
            service="python-cloud-debug",
            service_version="1.0.1",
            verbose=3,  # 0-error, 1-warning, 2-info, 3-debug
        )
    except (ValueError, NotImplementedError) as exc:
        logger.debug(exc)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_ROOT}/openapi.json")

if len(settings.BACKEND_CORS_ORIGINS) != 0:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_ROOT)
