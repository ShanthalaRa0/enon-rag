# orchestration/websocket_events.py
import os
import json
import logging

import redis


logger = logging.getLogger(__name__)


# =========================================================
# Redis Pub/Sub Client
# =========================================================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


# =========================================================
# Event Publisher
# =========================================================

def publish_event(
    workflow_id: str,
    event: str,
    data: dict = None,
):
    """
    Publish workflow event to Redis Pub/Sub.
    """

    try:

        payload = {
            "workflow_id": workflow_id,
            "event": event,
            "data": data or {},
        }

        redis_client.publish(
            f"workflow:{workflow_id}",
            json.dumps(payload)
        )

        logger.info(
            f"[EVENT PUBLISHED] "
            f"{workflow_id} "
            f"{event}"
        )

    except Exception as e:

        logger.exception(
            "[EVENT PUBLISH FAILED]"
        )

        raise e


# =========================================================
# Workflow Started Event
# =========================================================

def emit_pipeline_started(
    workflow_id: str,
    data: dict = None,
):
    publish_event(
        workflow_id=workflow_id,
        event="PIPELINE_STARTED",
        data=data,
    )


# =========================================================
# Workflow Stage Event
# =========================================================

def emit_pipeline_stage(
    workflow_id: str,
    stage: str,
    progress: int,
):
    publish_event(
        workflow_id=workflow_id,
        event="PIPELINE_STAGE",
        data={
            "stage": stage,
            "progress": progress,
        }
    )


# =========================================================
# Workflow Completed Event
# =========================================================

def emit_pipeline_completed(
    workflow_id: str,
):
    publish_event(
        workflow_id=workflow_id,
        event="PIPELINE_COMPLETED",
        data={
            "progress": 100
        }
    )


# =========================================================
# Workflow Failed Event
# =========================================================

def emit_pipeline_failed(
    workflow_id: str,
    error: str,
):
    publish_event(
        workflow_id=workflow_id,
        event="PIPELINE_FAILED",
        data={
            "error": error
        }
    )