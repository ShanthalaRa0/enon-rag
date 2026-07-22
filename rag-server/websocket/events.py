# websocket/events.py

import json
import logging

import redis


logger = logging.getLogger(__name__)


redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)


EVENT_CHANNEL = "workflow_events"


def publish_event(
    workflow_id: str,
    event: dict,
):
    """
    Publish workflow event to Redis.
    """

    payload = {
        "workflow_id": workflow_id,
        **event,
    }


    redis_client.publish(
        f"workflow:{workflow_id}",
        json.dumps(payload),
    )


# =========================================================
# Pipeline Events
# =========================================================


def emit_pipeline_stage(
    workflow_id: str,
    stage: str,
    progress: int,
):
    """
    Send pipeline stage update.
    """

    publish_event(
        workflow_id,
        {
            "type": "STAGE_UPDATE",
            "stage": stage,
            "progress": progress,
        },
    )


def emit_pipeline_completed(
    workflow_id: str,
):
    """
    Send workflow completed event.
    """

    publish_event(
        workflow_id,
        {
            "type": "PIPELINE_COMPLETED",
            "stage": "FINISHED",
            "progress": 100,
        },
    )


def emit_pipeline_failed(
    workflow_id: str,
    error: str,
):
    """
    Send workflow failure event.
    """

    publish_event(
        workflow_id,
        {
            "type": "PIPELINE_FAILED",
            "error": error,
        },
    )