from fastapi import APIRouter, HTTPException
import logging

from api.schemas.query_schema import QueryRequest
from services.retrieval_service import query_documents

from services.database_service import database_service


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/query")
async def query_route(request: QueryRequest):

    documents = database_service.get_all_documents()

    if not documents:
        return {
            "message": "No data exists to search",
            "results": []
        }

    try:

        result = query_documents(
            question=request.question,
            top_k=request.top_k
        )

        return {
            "message": "success",
            "results": result
        }

    except Exception as e:

        logger.exception("Query failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )