import os, json
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .state import AgentState, ReviewResult
from .policies import SUPPORT_POLICY

REVIEW_INSTRUCTIONS = (
    "You are a meticulous support QA reviewer. Read the draft and ensure it follows policy. "
    "Return STRICT JSON with keys: approved (boolean), feedback (string), reasons (array of strings). "
    "Reject if it overpromises refunds, lacks steps, or makes security mistakes."
)

def _offline_review(draft: str) -> ReviewResult:
    reasons: List[str] = []
    lower = draft.lower()
    if "refund" in lower and "cannot" not in lower and "approval" not in lower:
        reasons.append("Offered refund without approval.")
    if "sorry" not in lower and "thanks" not in lower:
        reasons.append("Tone may be too terse; add empathy.")
    if "step" not in lower and "1)" not in lower and "- " not in lower:
        reasons.append("Missing concrete steps.")
    approved = len(reasons) == 0
    fb = "Add empathy and concrete steps; mention refund approvals path." if not approved else "Looks good."
    return ReviewResult(approved=approved, feedback=fb, reasons=reasons)

def review(state: AgentState) -> Dict:
    draft = state.get("draft", "")
    use_llm = os.getenv("DRY_RUN_NO_LLM", "0") != "1" and os.getenv("OPENAI_API_KEY")

    if use_llm:
        llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
        system = SystemMessage(content=REVIEW_INSTRUCTIONS + "\n\n" + SUPPORT_POLICY)
        human = HumanMessage(content=f"Draft to review:\n\n{draft}")
        try:
            out = llm.invoke([system, human]).content.strip()
            # Be robust to extra text; find JSON object
            start = out.find("{")
            end = out.rfind("}")
            obj = json.loads(out[start:end+1]) if start!=-1 and end!=-1 else {}
            approved = bool(obj.get("approved", False))
            feedback = obj.get("feedback", "")
            reasons = obj.get("reasons", [])
            res = ReviewResult(approved=approved, feedback=feedback, reasons=reasons)
        except Exception:
            res = _offline_review(draft)
    else:
        res = _offline_review(draft)

    reviews_hist = list(state.get("reviews_history", [])) + [res.model_dump()]
    return {"review": res, "reviews_history": reviews_hist}
