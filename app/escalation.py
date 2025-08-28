import os, csv, datetime
from typing import Dict
from .state import AgentState

ESCALATION_CSV = "data/escalation_log.csv"

def route_after_review(state: AgentState) -> str:
    # Decide whether to finalize, retry, or escalate
    review = state.get("review")
    attempts = int(state.get("attempts", 0))
    if getattr(review, "approved", False):
        return "finalize"
    if attempts >= 2:
        return "escalate"
    return "refine"

def finalize(state: AgentState) -> Dict:
    return {"final_response": state.get("draft", ""), "escalated": False}

def escalate(state: AgentState) -> Dict:
    os.makedirs(os.path.dirname(ESCALATION_CSV), exist_ok=True)
    file_exists = os.path.exists(ESCALATION_CSV)
    with open(ESCALATION_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["timestamp","subject","description","category","attempts","drafts","reviews"])
        w.writerow([
            datetime.datetime.utcnow().isoformat(),
            state.get("subject",""),
            state.get("description",""),
            state.get("category",""),
            state.get("attempts",0),
            " ||| ".join(state.get("drafts_history", [])),
            " ||| ".join([str(r) for r in state.get("reviews_history", [])]),
        ])
    msg = (
        "This ticket requires human review. We've logged the details to data/escalation_log.csv "
        "including all failed drafts and reviewer feedback."
    )
    return {"final_response": msg, "escalated": True}
