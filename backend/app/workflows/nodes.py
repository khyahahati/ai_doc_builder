from state import SectionState
from backend.app.services.llm_service import llm_generate, llm_evaluate, llm_refine


# 1️⃣ First draft or retry
def generate_content(state: SectionState) -> SectionState:
    state.content = llm_generate(
        section_id=state.section_id,
        content=state.content
    )
    return state


# 2️⃣ Score content
def evaluate_content(state: SectionState) -> SectionState:
    result = llm_evaluate(state.content)
    state.score = result["score"]
    return state


# 3️⃣ Improve version
def refine_content(state: SectionState) -> SectionState:
    state.content = llm_refine(
        content=state.content,
        feedback=("Content scored low" if state.score else None),
        user_prompt=state.user_prompt
    )
    state.version += 1
    state.attempts += 1
    return state
