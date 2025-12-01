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
from ..services.llm_service import llm_refine
from google.api_core import exceptions as google_exceptions
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sections"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RefineIn(BaseModel):
    feedback: Optional[str] = None   # "like" | "dislike" | "generate"
    user_prompt: Optional[str] = None
    persist: Optional[bool] = True
    current_content: Optional[str] = None 


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
def refine_section(
    section_id: int,
    body: RefineIn,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Handle three flows:

    - feedback = "generate": full LangGraph workflow (generate + auto-refine).
    - feedback = "dislike": single refinement pass using llm_refine (no graph loop).
    - feedback = "like": no LLM, just persist current content if persist=True.
    """
    payload = verify_access_token(token)
    user_id = payload.get("user_id")

    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    proj = db.query(Project).filter(Project.id == sec.project_id).first()
    if not proj or proj.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # safety default
    persist_flag = bool(getattr(body, "persist", True))
    feedback = (body.feedback or "generate").lower()

    # -------------------------
    # 1) LOOKS GOOD / LIKE
    # -------------------------
    if feedback == "like":
        # Use the latest content coming from the UI if provided
        content_to_save = (body.current_content or sec.content or "")

        if persist_flag:
            try:
                version = sec.version + 1
                rev = Revision(
                    section_id=sec.id,
                    version=version,
                    content=content_to_save,
                    score=None,
                )
                db.add(rev)

                sec.content = content_to_save
                sec.version = version
                sec.status = "refined"
                db.add(sec)
                db.commit()
                db.refresh(sec)
            except Exception:
                db.rollback()
                logger.exception("Failed to persist 'like' content")
                raise HTTPException(status_code=500, detail="Failed to save approved content")

        return {
            "id": sec.id,
            "content": content_to_save,
            "version": sec.version,
            "score": None,
            "persisted": persist_flag,
        }

    # -------------------------
    # 2) NEEDS CHANGES / DISLIKE
    # -------------------------
    if feedback == "dislike":
        # Base text: prefer current content from UI, fall back to DB
        base_text = (body.current_content or sec.content or "")
        user_instruction = body.user_prompt or "Improve clarity and structure while preserving meaning."

        try:
            refined = llm_refine(
                content=base_text,
                improvement_focus=user_instruction,
                user_prompt=user_instruction,
            )
        except google_exceptions.ResourceExhausted:
            logger.warning("LLM quota exhausted on dislike-refine")
            raise HTTPException(status_code=503, detail="LLM quota exhausted — try again later.")
        except Exception:
            logger.exception("llm_refine failed on dislike")
            raise HTTPException(status_code=500, detail="Refinement failed")

        if persist_flag:
            try:
                version = sec.version + 1
                rev = Revision(
                    section_id=sec.id,
                    version=version,
                    content=refined,
                    score=None,
                )
                db.add(rev)

                sec.content = refined
                sec.version = version
                sec.status = "refined"
                db.add(sec)
                db.commit()
                db.refresh(sec)
            except Exception:
                db.rollback()
                logger.exception("Failed to persist refined content for dislike")
                raise HTTPException(status_code=500, detail="Failed to save refined content")

        # If not persisting, still return the refined text so the editor updates
        return {
            "id": sec.id,
            "content": refined,
            "version": sec.version + (1 if persist_flag else 0),
            "score": None,
            "persisted": persist_flag,
        }


    # -------------------------
    # 3) GENERATE / DEFAULT → use LangGraph
    # -------------------------

    # Build context (same as before)
    context_parts = []
    if body.user_prompt and str(body.user_prompt).strip():
        context_parts.append(str(body.user_prompt).strip())
    elif sec.content:
        preview = sec.content if len(sec.content) <= 2000 else sec.content[:2000]
        context_parts.append("Current content: " + preview)

    combined_context = "\n\n".join(context_parts).strip()

    state = SectionState(
        section_id=sec.id,
        section_title=sec.title,
        doc_type=proj.doc_type,
        content=sec.content,
        context_summary=combined_context,
        user_prompt=body.user_prompt,
        user_feedback="pending",
    )

    try:
        result = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)
    except google_exceptions.ResourceExhausted:
        logger.warning("LLM quota exhausted on generate")
        raise HTTPException(status_code=503, detail="LLM quota exhausted — try again later.")
    except Exception:
        logger.exception("Workflow invocation failed on generate")
        raise HTTPException(status_code=500, detail="Generation failed")

    if isinstance(result, dict):
        final_content = result.get("content")
        version = result.get("version", sec.version + 1)
        score = result.get("score")
    else:
        final_content = result.content
        version = result.version
        score = result.score

    if persist_flag:
        try:
            rev = Revision(
                section_id=sec.id,
                version=version,
                content=final_content,
                score=score,
            )
            db.add(rev)

            sec.content = final_content
            sec.version = version
            sec.status = "refined"
            db.add(sec)
            db.commit()
            db.refresh(sec)
        except Exception:
            db.rollback()
            logger.exception("Failed to persist generated content")
            raise HTTPException(status_code=500, detail="Failed to save generated content")

        return {
            "id": sec.id,
            "content": sec.content,
            "version": sec.version,
            "score": score,
            "persisted": True,
        }

    # preview-only path (you aren’t using this yet, but it’s here)
    return {
        "id": sec.id,
        "content": final_content,
        "version": version,
        "score": score,
        "persisted": False,
    }




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
