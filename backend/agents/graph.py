"""
LangGraph workflow:

  extraction -> completeness --(missing fields)--> END (ask user, resume at extraction next turn)
                             --(complete)--> qms_reasoning -> capa_recommendation -> summary -> END

The "loop" described in the assignment (completeness <-> extraction) happens ACROSS chat turns:
each user message re-enters at `extraction`, which merges new info into the persisted state,
then `completeness` re-checks. Once complete, it flows straight through reasoning, CAPA
recommendation, and summary.
"""
from langgraph.graph import StateGraph, END

from .state import ComplaintState
from .nodes import (
    extraction_node,
    completeness_node,
    qms_reasoning_node,
    capa_recommendation_node,
    summary_node,
)


def route_after_completeness(state: ComplaintState) -> str:
    return "qms_reasoning" if state.get("is_complete") else "end_turn"


def build_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node("extract_info", extraction_node)
    graph.add_node("completeness", completeness_node)
    graph.add_node("qms_reasoning", qms_reasoning_node)
    graph.add_node("capa_recommendation", capa_recommendation_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("extract_info")
    graph.add_edge("extract_info", "completeness")
    graph.add_conditional_edges(
        "completeness",
        route_after_completeness,
        {"qms_reasoning": "qms_reasoning", "end_turn": END},
    )
    graph.add_edge("qms_reasoning", "capa_recommendation")
    graph.add_edge("capa_recommendation", "summary")
    graph.add_edge("summary", END)

    return graph.compile()


complaint_graph = build_graph()
