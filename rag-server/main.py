from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.routes.upload_routes import router as upload_router
from api.routes.query_routes import router as query_router
from api.routes.status_routes import router as status_router
#from api.routes.websocket_routes import router as websocket_router
from websocket.router import router as websocket_router
from api.routes.workspace_routes import router as workspace_router

from services.workspace_service import (
    ensure_workspace_directories,
)

from api.middleware.logging_middleware import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_workspace_directories()

    yield


app = FastAPI(
    title="RAG Server",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(status_router)
app.include_router(websocket_router)
app.include_router(workspace_router)

@app.get("/")
def root():

    return {
        "message": "RAG Server Running"
    }