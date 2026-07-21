# websocket/router.py

import json
import logging

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)


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

            data = await websocket.receive_text()

            logger.info(
                f"[WS MESSAGE] {workflow_id}: {data}"
            )


    except WebSocketDisconnect:

        manager.disconnect(
            workflow_id,
            websocket,
        )


    except Exception as e:

        logger.exception(
            "[WS ERROR]"
        )

        manager.disconnect(
            workflow_id,
            websocket,
        )