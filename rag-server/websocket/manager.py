import asyncio
import logging

from collections import defaultdict

from fastapi import WebSocket

from websocket.redis_listener import listen

logger = logging.getLogger(__name__)


class WorkflowConnectionManager:

    def __init__(self):

        self.connections = defaultdict(list)

        self.listener_tasks = {}


    async def connect(
        self,
        workflow_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.connections[workflow_id].append(
            websocket
        )

        #
        # Start ONE Redis listener
        #

        if workflow_id not in self.listener_tasks:

            logger.info(
                f"[LISTENER STARTED] {workflow_id}"
            )

            self.listener_tasks[
                workflow_id
            ] = asyncio.create_task(
                listen(
                    workflow_id,
                    lambda message:
                        self.broadcast(
                            workflow_id,
                            message,
                        ),
                )
            )

        logger.info(
            f"[WS CONNECTED] {workflow_id}"
        )


    async def disconnect(
        self,
        workflow_id: str,
        websocket: WebSocket,
    ):

        if websocket in self.connections[workflow_id]:

            self.connections[workflow_id].remove(
                websocket
            )

        #
        # Last client disconnected
        #

        if not self.connections[workflow_id]:

            del self.connections[workflow_id]

            task = self.listener_tasks.pop(
                workflow_id,
                None,
            )

            if task:

                task.cancel()

                try:

                    await task

                except asyncio.CancelledError:

                    pass

                logger.info(
                    f"[LISTENER STOPPED] {workflow_id}"
                )

        logger.info(
            f"[WS DISCONNECTED] {workflow_id}"
        )


    async def broadcast(
        self,
        workflow_id: str,
        message: dict,
    ):

        logger.info(
            f"[BROADCAST] {workflow_id}"
        )

        logger.info(
            f"[CLIENTS] {len(self.connections.get(workflow_id, []))}"
        )

        dead_connections = []

        for websocket in self.connections.get(
            workflow_id,
            [],
        ):

            try:

                await websocket.send_json(message)

                logger.info("[MESSAGE SENT]")

            except Exception:

                logger.exception(
                    "[SEND FAILED]"
                )

                dead_connections.append(
                    websocket
                )

        for websocket in dead_connections:

            await self.disconnect(
                workflow_id,
                websocket,
            )


manager = WorkflowConnectionManager()