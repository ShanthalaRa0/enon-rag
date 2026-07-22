from fastapi import FastAPI

from api.routes.upload_routes import router as upload_router
from api.routes.query_routes import router as query_router
from api.routes.status_routes import router as status_router
#from api.routes.websocket_routes import router as websocket_router
from websocket.router import router as websocket_router

from api.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="RAG Server",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(status_router)
app.include_router(websocket_router)


@app.get("/")
def root():

    return {
        "message": "RAG Server Running"
    }