# orchestration/pipeline_status.py
import os
import json
import logging
from datetime import datetime

import redis


logger = logging.getLogger(__name__)


# =========================================================
# Redis Connection
# =========================================================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


# =========================================================
# Redis Key Builder
# =========================================================

def build_pipeline_key(
    workflow_id: str,
):
    return f"pipeline_status:{workflow_id}"


# =========================================================
# Update Pipeline Status
# =========================================================

def update_pipeline_status(
    workflow_id: str,
    status: str,
    stage: str = None,
    progress: int = None,
    error: str = None,
    file_name: str = None,
    created_at: str = None,
):
    """
    Persist workflow status in Redis.
    """

    try:

        redis_key = build_pipeline_key(
            workflow_id
        )

        # ---------------------------------------------
        # Fetch existing state
        # ---------------------------------------------

        existing = redis_client.get(redis_key)

        if existing:
            payload = json.loads(existing)
        else:
            payload = {}

        # ---------------------------------------------
        # Update fields
        # ---------------------------------------------

        payload["workflow_id"] = workflow_id
        payload["status"] = status

        if stage is not None:
            payload["stage"] = stage

        if progress is not None:
            payload["progress"] = progress

        if error is not None:
            payload["error"] = error

        if file_name is not None:
            payload["file_name"] = file_name

        if created_at is not None:
            payload["created_at"] = created_at

        payload["updated_at"] = str(
            datetime.utcnow()
        )

        # ---------------------------------------------
        # Save back to Redis
        # ---------------------------------------------

        redis_client.set(
            redis_key,
            json.dumps(payload)
        )

        logger.info(
            f"[STATUS UPDATED] {workflow_id} "
            f"{status} {stage}"
        )

    except Exception as e:

        logger.exception(
            "[PIPELINE STATUS UPDATE FAILED]"
        )

        raise e


# =========================================================
# Get Pipeline Status
# =========================================================

def get_pipeline_status(
    workflow_id: str,
):
    """
    Retrieve workflow state from Redis.
    """

    try:

        redis_key = build_pipeline_key(
            workflow_id
        )

        data = redis_client.get(redis_key)

        if not data:

            return {
                "workflow_id": workflow_id,
                "status": "UNKNOWN",
            }

        return json.loads(data)

    except Exception as e:

        logger.exception(
            "[PIPELINE STATUS FETCH FAILED]"
        )

        raise e


# =========================================================
# Delete Pipeline Status
# =========================================================

def delete_pipeline_status(
    workflow_id: str,
):
    """
    Remove workflow state.
    """

    try:

        redis_key = build_pipeline_key(
            workflow_id
        )

        redis_client.delete(redis_key)

        logger.info(
            f"[STATUS DELETED] {workflow_id}"
        )

    except Exception as e:

        logger.exception(
            "[PIPELINE STATUS DELETE FAILED]"
        )

        raise e