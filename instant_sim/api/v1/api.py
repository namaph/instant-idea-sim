from fastapi import APIRouter

from instant_sim.api.v1.endpoint import home, simulator, visualizer

api_router = APIRouter()
api_router.include_router(home.router, tags=["home"])
api_router.include_router(simulator.router, tags=["simulator"])
api_router.include_router(visualizer.router, tags=["visualizer"])
