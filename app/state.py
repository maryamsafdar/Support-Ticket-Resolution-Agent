from typing import List, Optional, Literal, TypedDict, Dict, Any
from pydantic import BaseModel

Category = Literal["Billing", "Technical", "Security", "General"]

class ReviewResult(BaseModel):
    approved: bool
    feedback: str = ""
    reasons: List[str] = []

class AgentState(TypedDict):
    # Input
    subject: str
    description: str

    # Derived
    category: Category
    retrieval_query: str
    context_docs: List[str]

    # Drafts / Reviews
    draft: str
    review: ReviewResult
    attempts: int

    # Trace
    drafts_history: List[str]
    reviews_history: List[Dict[str, Any]]

    # Output
    final_response: str
    escalated: bool
