from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

active_connections = []


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):

    await websocket.accept()

    active_connections.append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            await websocket.send_text(
                f"Job {job_id}: {data}"
            )

    except WebSocketDisconnect:

        active_connections.remove(websocket)

        logger.info(f"WebSocket disconnected: {job_id}")