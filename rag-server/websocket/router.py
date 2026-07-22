import logging

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from websocket.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket(
    "/ws/workflow/{workflow_id}"
)
async def workflow_listener(
    websocket: WebSocket,
    workflow_id: str,
):

    await manager.connect(
        workflow_id,
        websocket,
    )

    try:

        while True:

            #
            # Keep socket alive
            #

            await websocket.receive_text()

    except WebSocketDisconnect:

        await manager.disconnect(
            workflow_id,
            websocket,
        )

    except Exception:

        logger.exception(
            "[WS ERROR]"
        )

        await manager.disconnect(
            workflow_id,
            websocket,
        )