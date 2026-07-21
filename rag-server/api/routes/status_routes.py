from fastapi import APIRouter, HTTPException
import logging

from orchestration.pipeline_status import get_pipeline_status

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/pipeline/status/{job_id}")
async def pipeline_status(job_id: str):

    try:

        status = get_pipeline_status(job_id)

        return status

    except Exception as e:

        logger.exception("Status fetch failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )