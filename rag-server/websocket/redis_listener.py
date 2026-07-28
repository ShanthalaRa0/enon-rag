import asyncio
import json
import logging
import os

import redis.asyncio as redis

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


async def listen(
    workflow_id: str,
    callback,
):
    """
    Listen for Redis Pub/Sub events for a workflow
    and forward them to the supplied callback.
    """

    channel = f"workflow:{workflow_id}"

    logger.info(
        f"[LISTENER STARTED] {workflow_id}"
    )

    pubsub = redis_client.pubsub()

    await pubsub.subscribe(channel)

    logger.info(
        f"[REDIS SUBSCRIBED] {channel}"
    )

    try:

        while True:

            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1,
            )

            if message:

                logger.info(
                    f"[REDIS RECEIVED] {message['data']}"
                )

                payload = json.loads(
                    message["data"]
                )

                logger.info(
                    "[CALLBACK]"
                )

                await callback(payload)

            await asyncio.sleep(0.05)

    except asyncio.CancelledError:

        logger.info(
            f"[LISTENER STOPPED] {workflow_id}"
        )

    finally:

        await pubsub.unsubscribe(channel)

        await pubsub.close()