import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .state import AgentState

BASE_INSTRUCTIONS = (
    "You are a support agent. Write a clear, empathetic, and actionable reply grounded ONLY in the provided context. "
    "Do NOT offer refunds/credits or share secrets. Provide steps, ask for verification where needed. "
    "End with an offer of further help."
)

def _template_draft(state: AgentState, context: List[str]) -> str:
    ctx = "\n\n---\n".join(context[:3]) if context else "No additional internal context."
    return (
        f"Hello,\n\nThanks for reaching out about '{state.get('subject','')}'. "
        "Based on our internal notes, here are some steps to try:\n\n"
        "1) Reinstall/update the app if it's a Technical issue\n"
        "2) For Billing questions, our policy requires approval for refunds. Please confirm your account email.\n"
        "3) For Security concerns, immediately reset your password and enable 2FA.\n\n"
        "Context consulted:\n" + ctx + "\n\n"
        "If the issue persists, reply with any error codes or screenshots so we can assist further."
    )

def draft(state: AgentState) -> Dict:
    use_llm = os.getenv("DRY_RUN_NO_LLM", "0") != "1" and os.getenv("OPENAI_API_KEY")
    context = state.get("context_docs", [])
    if use_llm:
        llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)
        system = SystemMessage(content=BASE_INSTRUCTIONS)
        ticket = f"Category: {state.get('category')}\nSubject: {state.get('subject')}\nDescription: {state.get('description')}"
        ctx = "\n\n--- Context Doc ---\n".join(context) if context else "No additional internal context."
        human = HumanMessage(content=f"""{ticket}

[Internal Context]
{ctx}

Please write the customer-facing reply now.""")
        try:
            reply = llm.invoke([system, human]).content.strip()
        except Exception:
            reply = _template_draft(state, context)
    else:
        reply = _template_draft(state, context)

    drafts_hist = list(state.get("drafts_history", [])) + [reply]
    return {"draft": reply, "drafts_history": drafts_hist}
