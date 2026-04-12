from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Any

from . import shared

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/search")
async def search(req: QueryRequest) -> List[Any]:
    results = shared.vectorstore.similarity_search(req.query, k=req.k)
    return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]
