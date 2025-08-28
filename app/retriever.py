from typing import Dict, List, Any
from .state import AgentState
from .utils.rag_index import RAGIndex

_INDEX = None

def _get_index() -> RAGIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = RAGIndex(base_dir="data/knowledge")
    return _INDEX

def _extract_feedback(state: AgentState) -> str:
    rv: Any = state.get("review")
    if isinstance(rv, dict):
        return str(rv.get("feedback", ""))
    # pydantic model ReviewResult or similar object
    if hasattr(rv, "feedback"):
        try:
            return str(getattr(rv, "feedback", "") or "")
        except Exception:
            return ""
    return ""

def retrieve(state: AgentState) -> Dict:
    category = state["category"]
    query = state.get("retrieval_query") or (state.get("subject", "") + "\n" + state.get("description", ""))
    idx = _get_index()
    docs: List[str] = idx.query(category, query, k=4)
    return {"context_docs": docs}

def refine(state: AgentState) -> Dict:
    idx = _get_index()
    fb = _extract_feedback(state)
    rq = state.get("retrieval_query", "") or ""
    new_q = idx.refine_query(rq, fb)
    docs = idx.query(state["category"], new_q, k=4)
    return {"retrieval_query": new_q, "context_docs": docs, "attempts": state.get("attempts", 0) + 1}
