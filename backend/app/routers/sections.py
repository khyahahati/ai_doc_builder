from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.project import Project
from ..models.revision import Revision
from ..models.section import Section
from ..utils.jwt_utils import verify_access_token
from ..workflows.graph import DEFAULT_GRAPH_CONFIG, graph
from ..workflows.state import SectionState

router = APIRouter(tags=["Sections"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RefineIn(BaseModel):
    feedback: Optional[str] = None   # "like" or "dislike" or "generate" or "like"
    user_prompt: Optional[str] = None
    persist: Optional[bool] = True


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from ..models.user import User as UserModel
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/sections/{section_id}")
def get_section(section_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Get single section.
    """
    # verify token owner (light check)
    payload = verify_access_token(token)
    user_id = payload.get("user_id")

    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    proj = db.query(Project).filter(Project.id == sec.project_id).first()
    if not proj or proj.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {"id": sec.id, "title": sec.title, "content": sec.content, "version": sec.version, "status": sec.status}


from google.api_core import exceptions as google_exceptions  # add to top of file near other imports
import logging

logger = logging.getLogger(__name__)

@router.post("/sections/{section_id}/refine")
def refine_section(section_id: int, body: RefineIn, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Refine a section using the LangGraph workflow and Gemini.
    Body may contain:
      - feedback: "like" | "dislike" | "generate"
      - user_prompt: optional instruction overriding stored summary/guidance
      - persist: bool (if True, save the generated content into DB)
    """
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    proj = db.query(Project).filter(Project.id == sec.project_id).first()
    if not proj or proj.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Build context (prefer explicit user_prompt; then stored summary/guidance; finally existing content)
    context_parts = []
    if body.user_prompt and str(body.user_prompt).strip():
        context_parts.append(str(body.user_prompt).strip())
    else:
        if hasattr(sec, "summary") and sec.summary:
            context_parts.append(str(sec.summary).strip())
        if hasattr(sec, "guidance") and sec.guidance:
            context_parts.append("Guidance: " + str(sec.guidance).strip())
        if not context_parts and sec.content:
            preview = sec.content if len(sec.content) <= 2000 else sec.content[:2000]
            context_parts.append("Current content: " + preview)

    combined_context = "\n\n".join(context_parts).strip()

    # Build state for LangGraph
    state = SectionState(
        section_id=sec.id,
        section_title=sec.title,
        doc_type=proj.doc_type,
        content=sec.content,
        context_summary=combined_context,
        user_prompt=body.user_prompt,
        user_feedback=body.feedback or "pending"
    )

    # debug print
    try:
        logger.debug("=== CONTEXT SUMMARY SENT TO MODEL ===\n%s\n=== END CONTEXT ===", combined_context[:1600])
    except Exception:
        pass

    # Invoke workflow exactly once and handle LLM errors
    try:
        result = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)
    except Exception as e:
        # If it's a quota / rate-limit type error from Google client, surface it clearly
        if isinstance(e, google_exceptions.ResourceExhausted):
            logger.warning("LLM quota exhausted: %s", e)
            raise HTTPException(status_code=503, detail="LLM quota exhausted — try again later.")
        logger.exception("Workflow invocation failed")
        raise HTTPException(status_code=500, detail="Generation failed")

    if isinstance(result, dict):
        final_content = result.get("content")
        version = result.get("version", sec.version + 1)
        score = result.get("score")
    else:
        final_content = result.content
        version = result.version
        score = result.score

    persist_flag = bool(getattr(body, "persist", True))

    if not persist_flag:
        # Return preview only — do not save revision or update DB
        return {"id": sec.id, "content": final_content, "version": version, "score": score, "persisted": False}

    # Persist: create revision and update section (existing behavior)
    try:
        rev = Revision(section_id=sec.id, version=version, content=final_content, score=score)
        db.add(rev)

        sec.content = final_content
        sec.version = version
        sec.status = "refined"
        db.add(sec)
        db.commit()
        db.refresh(sec)
    except Exception:
        logger.exception("Failed to persist refined content")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save refined content")

    return {"id": sec.id, "content": sec.content, "version": sec.version, "score": score, "persisted": True}



@router.get("/sections/{section_id}/revisions")
def list_revisions(section_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    proj = db.query(Project).filter(Project.id == sec.project_id).first()
    if not proj or proj.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    revs = db.query(Revision).filter(Revision.section_id == section_id).order_by(Revision.created_at.desc()).all()
    return [{"id": r.id, "version": r.version, "score": r.score, "created_at": r.created_at} for r in revs]
