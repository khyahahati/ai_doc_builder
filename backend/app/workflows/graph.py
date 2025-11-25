from langgraph.graph import END, StateGraph

from .nodes import evaluate_content, generate_content, refine_content
from .state import SectionState


def decision_router(state: SectionState):
    # Stop if user liked the result
    if state.user_feedback == "like":
        return END

    # Retry if user disliked
    if state.user_feedback == "dislike":
        return "refine_content"

    # Stop if attempts reached limit
    if state.attempts >= state.max_attempts:
        return END

    # Retry if score is low
    if state.score is not None and state.score < 7.5:
        return "refine_content"

    # Otherwise stop
    return END


workflow = StateGraph(SectionState)

workflow.add_node("generate_content", generate_content)
workflow.add_node("evaluate_content", evaluate_content)
workflow.add_node("refine_content", refine_content)

workflow.set_entry_point("generate_content")

workflow.add_edge("generate_content", "evaluate_content")

workflow.add_conditional_edges(
    "evaluate_content",
    decision_router,
    {
        "refine_content": "refine_content",
        END: END
    }
)

workflow.add_edge("refine_content", "evaluate_content")

graph = workflow.compile()

DEFAULT_GRAPH_CONFIG = {"recursion_limit": 100}
