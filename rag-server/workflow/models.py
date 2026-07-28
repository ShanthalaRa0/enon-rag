# Pydantic models - This guarantees every event has the same shape.
from pydantic import BaseModel

from workflow.event_types import (
    WorkflowEventType,
    WorkflowStatus,
    WorkflowStage,
)


class WorkflowEvent(BaseModel):

    workflow_id: str

    type: WorkflowEventType

    status: WorkflowStatus

    stage: WorkflowStage

    progress: int

    message: str

    error: str | None = None