import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .state import AgentState

CATS = ["Billing", "Technical", "Security", "General"]

def _heuristic(subject: str, description: str) -> str:
    text = f"{subject} {description}".lower()
    if any(k in text for k in ["invoice", "refund", "charge", "billing", "payment", "credit card"]):
        return "Billing"
    if any(k in text for k in ["password", "2fa", "breach", "phishing", "compromise", "security"]):
        return "Security"
    if any(k in text for k in ["error", "bug", "crash", "login", "install", "api", "mobile", "ios", "android"]):
        return "Technical"
    return "General"

def classify(state: AgentState) -> Dict:
    subject = state.get("subject", "")
    description = state.get("description", "")
    use_llm = os.getenv("DRY_RUN_NO_LLM", "0") != "1" and os.getenv("OPENAI_API_KEY")

    if use_llm:
        llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
        system = SystemMessage(content=(
            "Classify the support ticket into one of: Billing, Technical, Security, General. "
            "Return ONLY the category word."
        ))
        human = HumanMessage(content=f"Subject: {subject}\nDescription: {description}")
        try:
            out = llm.invoke([system, human]).content.strip()
            cat = out.split()[0]
            if cat not in CATS:
                cat = _heuristic(subject, description)
        except Exception:
            cat = _heuristic(subject, description)
    else:
        cat = _heuristic(subject, description)

    retrieval_query = f"{subject}\n\n{description}"
    return {
        "category": cat,
        "retrieval_query": retrieval_query
    }
