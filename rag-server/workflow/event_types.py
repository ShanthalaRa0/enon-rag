#  enums

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
    UPLOAD = "UPLOAD"

    TEXT_EXTRACTION = "TEXT_EXTRACTION"

    CHUNKING = "CHUNKING"

    EMBEDDING = "EMBEDDING"

    VECTOR_STORE = "VECTOR_STORE"

    FINISHED = "FINISHED"