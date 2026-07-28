from workflow.event_factory import (
    stage_event,
    completed_event,
    failed_event,
    started_event,
)


import redis
import json
import os


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)



def publish(event):

    redis_client.publish(

        f"workflow:{event.workflow_id}",

        event.model_dump_json(),

    )



def emit_pipeline_started(
    workflow_id: str,
):

    publish(

        started_event(
            workflow_id
        )

    )



def emit_pipeline_stage(
    workflow_id,
    stage,
    progress,
    message,
):

    publish(

        stage_event(
            workflow_id,
            stage,
            progress,
            message,
        )

    )



def emit_pipeline_completed(
    workflow_id,
):

    publish(

        completed_event(
            workflow_id
        )

    )



def emit_pipeline_failed(
    workflow_id,
    stage,
    progress,
    error,
):

    publish(

        failed_event(
            workflow_id,
            stage,
            progress,
            error,
        )

    )