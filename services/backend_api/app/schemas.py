"""
Pydantic Schemas for API data validation
"""
from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """Request model for a user query, including filters and session state."""
    query: str
    session_id: str
    sources: Optional[List[str]] = None
    # Add date filters here in the future if desired, e.g.,
    # start_date: Optional[str] = None
    # end_date: Optional[str] = None
