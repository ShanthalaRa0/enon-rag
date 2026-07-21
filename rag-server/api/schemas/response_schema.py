from pydantic import BaseModel
from typing import List, Dict, Any


class QueryResponse(BaseModel):

    question: str
    answer: str
    retrieved_chunks: List[Dict[str, Any]]