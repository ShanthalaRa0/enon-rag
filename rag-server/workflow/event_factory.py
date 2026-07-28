# creates events

from workflow.models import WorkflowEvent

from workflow.event_types import *

def started_event(
    workflow_id: str,
):

    return WorkflowEvent(

        workflow_id=workflow_id,

        type=WorkflowEventType.STARTED,

        status=WorkflowStatus.RUNNING,

        stage=WorkflowStage.UPLOAD,

        progress=0,

        message="Workflow started.",

    )

def stage_event(
    workflow_id: str,
    stage: WorkflowStage,
    progress: int,
    message: str,
):

    return WorkflowEvent(
        workflow_id=workflow_id,

        type=WorkflowEventType.STAGE_UPDATE,

        status=WorkflowStatus.RUNNING,

        stage=stage,

        progress=progress,

        message=message,
    )


def completed_event(
    workflow_id: str,
):

    return WorkflowEvent(
        workflow_id=workflow_id,

        type=WorkflowEventType.COMPLETED,

        status=WorkflowStatus.COMPLETED,

        stage=WorkflowStage.FINISHED,

        progress=100,

        message="Workflow completed successfully.",
    )


def failed_event(
    workflow_id: str,
    error: str,
    stage: WorkflowStage = WorkflowStage.FINISHED,
    progress: int = 0,
):

    return WorkflowEvent(
        workflow_id=workflow_id,

        type=WorkflowEventType.FAILED,

        status=WorkflowStatus.FAILED,

        stage=stage,

        progress=progress,

        message="Workflow failed.",

        error=error,
    )