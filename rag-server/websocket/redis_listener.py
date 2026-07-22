import asyncio
import json
import logging
import os

import redis

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

    channel = f"workflow:{workflow_id}"

    pubsub = redis_client.pubsub()

    pubsub.subscribe(channel)

    logger.info(f"[REDIS SUBSCRIBED] {channel}")

    try:

        while True:

            message = pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1,
            )

            if message:

                payload = json.loads(
                    message["data"]
                )

                await callback(payload)

            await asyncio.sleep(0.05)

    except asyncio.CancelledError:

        logger.info(
            f"[REDIS STOPPED] {workflow_id}"
        )

    finally:

        pubsub.unsubscribe(channel)

        pubsub.close()