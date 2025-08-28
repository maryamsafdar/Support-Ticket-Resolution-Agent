import os
from dotenv import load_dotenv #ignore
from langgraph.graph import StateGraph, START, END #ignore

from app.state import AgentState
from app.classifier import classify
from app.retriever import retrieve, refine
from app.drafter import draft
from app.reviewer import review
from app.escalation import route_after_review, finalize, escalate

# Load .env if present
load_dotenv()

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("classify", classify)
    graph.add_node("retrieve", retrieve)
    graph.add_node("draft", draft)
    graph.add_node("review", review)
    graph.add_node("refine", refine)
    graph.add_node("finalize", finalize)
    graph.add_node("escalate", escalate)

    # Edges
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "draft")
    graph.add_edge("draft", "review")
    graph.add_conditional_edges("review", route_after_review, {
        "finalize": "finalize",
        "refine": "refine",
        "escalate": "escalate"
    })
    graph.add_edge("refine", "draft")
    graph.add_edge("finalize", END)
    graph.add_edge("escalate", END)

    # Let the LangGraph dev runtime handle checkpointing; just compile normally.
    return graph.compile()

# The LangGraph CLI will look for a compiled `graph` variable.
graph = build_graph()
