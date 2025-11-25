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
    feedback: Optional[str] = None   # "like" or "dislike" or None
    user_prompt: Optional[str] = None


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


@router.post("/sections/{section_id}/refine")
def refine_section(section_id: int, body: RefineIn, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Refine a section using the LangGraph workflow and Gemini. The body may contain:
    - feedback: "like" or "dislike"
    - user_prompt: instruction for refinement
    """
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    proj = db.query(Project).filter(Project.id == sec.project_id).first()
    if not proj or proj.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Build the state and set feedback / prompt
    state = SectionState(
        section_id=sec.id,
        section_title=sec.title,
        doc_type=proj.doc_type,
        content=sec.content,
        user_prompt=body.user_prompt,
        user_feedback=body.feedback or "pending"
    )

    result = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)
    if isinstance(result, dict):
        final_content = result.get("content")
        version = result.get("version", sec.version + 1)
        score = result.get("score")
    else:
        final_content = result.content
        version = result.version
        score = result.score

    # save revision
    rev = Revision(section_id=sec.id, version=version, content=final_content, score=score)
    db.add(rev)

    # update section
    sec.content = final_content
    sec.version = version
    sec.status = "refined"
    db.add(sec)
    db.commit()
    db.refresh(sec)

    return {"id": sec.id, "content": sec.content, "version": sec.version, "score": score}


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
