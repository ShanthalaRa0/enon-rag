from fastapi import APIRouter, HTTPException
import logging

from api.schemas.query_schema import QueryRequest
from services.retrieval_service import query_documents

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/query")
async def query_route(request: QueryRequest):

    try:

        result = query_documents(
            question=request.question,
            top_k=request.top_k
        )

        return result

    except Exception as e:

        logger.exception("Query failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )