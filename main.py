from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_routes.websockets import websocket_router
from app.api_routes.healthcheck import healthcheck_router

app = FastAPI()

app.include_router(healthcheck_router)

app.include_router(websocket_router, prefix="/ws")
