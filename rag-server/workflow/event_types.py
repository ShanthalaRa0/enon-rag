# enums

from enum import Enum


class WorkflowStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowEventType(str, Enum):
    STARTED = "PIPELINE_STARTED"
    STAGE_UPDATE = "STAGE_UPDATE"
    COMPLETED = "PIPELINE_COMPLETED"
    FAILED = "PIPELINE_FAILED"


class WorkflowStage(str, Enum):
    IDLE = "IDLE"

    UPLOADING = "UPLOADING"

    EXTRACTING = "EXTRACTING"

    TRANSLATING = "TRANSLATING"

    CHUNKING = "CHUNKING"

    EMBEDDING = "EMBEDDING"

    STORING = "STORING"

    COMPLETE = "COMPLETE"

    FAILED = "FAILED"