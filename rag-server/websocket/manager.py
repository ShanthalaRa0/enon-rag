# websocket/manager.py

import logging

from collections import defaultdict

from fastapi import WebSocket


logger = logging.getLogger(__name__)


class WorkflowConnectionManager:

    def __init__(self):

        # {
        #   workflow_id: [
        #       websocket1,
        #       websocket2
        #   ]
        # }

        self.connections = defaultdict(list)


    async def connect(
        self,
        workflow_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.connections[workflow_id].append(
            websocket
        )

        logger.info(
            f"[WS CONNECTED] {workflow_id}"
        )


    def disconnect(
        self,
        workflow_id: str,
        websocket: WebSocket,
    ):

        if websocket in self.connections[workflow_id]:

            self.connections[workflow_id].remove(
                websocket
            )

        if not self.connections[workflow_id]:

            del self.connections[workflow_id]


        logger.info(
            f"[WS DISCONNECTED] {workflow_id}"
        )


    async def broadcast(
        self,
        workflow_id: str,
        message: dict,
    ):

        dead_connections = []


        for websocket in self.connections.get(
            workflow_id,
            []
        ):

            try:

                await websocket.send_json(
                    message
                )

            except Exception:

                dead_connections.append(
                    websocket
                )


        for websocket in dead_connections:

            self.disconnect(
                workflow_id,
                websocket,
            )


manager = WorkflowConnectionManager()