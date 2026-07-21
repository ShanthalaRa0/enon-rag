from pydantic import BaseModel


class UploadResponse(BaseModel):

    status: str
    job_id: str
    workflow_id: str
    pipeline: str