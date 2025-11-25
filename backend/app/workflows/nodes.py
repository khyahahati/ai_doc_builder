from .state import SectionState
from ..services.llm_service import (
    llm_evaluate,
    llm_generate_section,
    llm_refine,
    llm_refine_outline,
)

# ✅ NEW — refine user outline BEFORE content generation
def refine_outline(state: SectionState) -> SectionState:
    if not state.raw_outline:
        return state  # nothing to refine

    state.refined_outline = llm_refine_outline(
        raw_outline=state.raw_outline,
        doc_type=state.doc_type
    )

    return state


# ✅ Node 1 — generate content based on section title + doc type
def generate_content(state: SectionState) -> SectionState:
    state.content = llm_generate_section(
        section_title=state.section_title,
        doc_type=state.doc_type,
        context_summary=state.context_summary or ""
    )
    return state

# ✅ Node 2 — evaluate and store improvement direction
def evaluate_content(state: SectionState) -> SectionState:
    result = llm_evaluate(state.content)
    state.score = result["score"]
    state.user_prompt = result["improvement_focus"]
    return state

# ✅ Node 3 — refine based on detected issues or user dislike
def refine_content(state: SectionState) -> SectionState:
    state.content = llm_refine(
        content=state.content,
        improvement_focus=state.user_prompt,
        user_prompt=state.user_prompt
    )
    state.version += 1
    state.attempts += 1
    return state

