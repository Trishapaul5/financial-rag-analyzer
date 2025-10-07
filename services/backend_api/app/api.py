"""
FastAPI router for the RAG endpoints
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from .core import RAGEngine
from .schemas import QueryRequest

router = APIRouter()
rag_engine = RAGEngine()

@router.post("/query/stream")
async def stream_query(request: QueryRequest):
    """
    Receives a query with filters and streams the RAG chain's response.
    """
    return StreamingResponse(
        rag_engine.stream_query(
            query=request.query, 
            session_id=request.session_id,
            sources=request.sources
        ),
        media_type="text/event-stream"
    )

@router.get("/db/stats")
async def get_db_stats():
    """Returns statistics about the documents in the vector database."""
    return rag_engine.get_db_stats()
