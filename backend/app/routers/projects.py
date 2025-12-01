from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.project import Project
from ..models.revision import Revision
from ..models.section import Section
from ..models.user import User
from ..services.export_service import export_to_docx, export_to_pptx
from ..utils.jwt_utils import verify_access_token
from ..workflows.graph import DEFAULT_GRAPH_CONFIG, graph
from ..workflows.state import SectionState

router = APIRouter(prefix="/projects", tags=["Projects"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---- simple request bodies (replace with your schemas if available) ----
class ProjectCreate(BaseModel):
    title: str
    doc_type: str  # "docx" or "pptx"


class OutlineIn(BaseModel):
    sections: List[str]


# ---- helper to get current user (same logic as auth router) ----
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    from ..models.user import User as UserModel
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new project (title + doc_type)
    """
    if payload.doc_type not in ("docx", "pptx"):
        raise HTTPException(status_code=400, detail="doc_type must be 'docx' or 'pptx'")

    project = Project(title=payload.title, doc_type=payload.doc_type, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)

    return {"id": project.id, "title": project.title, "doc_type": project.doc_type, "created_at": project.created_at}


@router.get("/my", response_model=List[dict])
def list_my_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List projects for the logged in user.
    """
    projects = db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.created_at.desc()).all()
    out = []
    for p in projects:
        out.append({"id": p.id, "title": p.title, "doc_type": p.doc_type, "created_at": p.created_at})
    return out


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # include sections
    sections = db.query(Section).filter(Section.project_id == project.id).order_by(Section.id).all()
    sections_list = [{"id": s.id, "title": s.title, "version": s.version, "status": s.status} for s in sections]
    return {"id": project.id, "title": project.title, "doc_type": project.doc_type, "sections": sections_list, "created_at": project.created_at}


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}


@router.post("/{project_id}/outline", status_code=status.HTTP_201_CREATED)
def submit_outline(project_id: int, payload: OutlineIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Submit outline (list of section titles) for a project.
    Creates section rows (pending status).
    """
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # delete existing sections for a clean replace (optional)
    existing = db.query(Section).filter(Section.project_id == project_id).all()
    for e in existing:
        db.delete(e)
    db.commit()

    created = []
    for title in payload.sections:
        sec = Section(project_id=project_id, title=title, status="pending")
        db.add(sec)
        db.commit()
        db.refresh(sec)
        created.append({"id": sec.id, "title": sec.title})

    return {"sections": created}


@router.get("/{project_id}/sections")
def list_sections(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    sections = db.query(Section).filter(Section.project_id == project_id).order_by(Section.id).all()
    return [{"id": s.id, "title": s.title, "content": s.content, "version": s.version, "status": s.status} for s in sections]


@router.post("/{project_id}/generate")
def generate_project_content(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generate document content for all sections using LangGraph + Gemini.
    Loops through sections where status != 'generated' and invokes the graph for each.
    Saves content and creates a Revision entry.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sections = db.query(Section).filter(Section.project_id == project_id).order_by(Section.id).all()
    if not sections:
        raise HTTPException(status_code=400, detail="No sections found to generate")

    generated = {}
    for sec in sections:
        # create state for the graph
        state = SectionState(
            section_id=sec.id,
            section_title=sec.title,
            doc_type=project.doc_type,
            content=sec.content,
            context_summary=f"Project: {project.title}"
        )

        result = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)
        # langgraph returns dict by default in your setup; handle both
        if isinstance(result, dict):
            final_content = result.get("content")
            version = result.get("version", sec.version)
            score = result.get("score")
        else:
            # pydantic object
            final_content = result.content
            version = result.version
            score = result.score

        # save
        sec.content = final_content
        sec.version = version
        sec.status = "generated"
        db.add(sec)

        # create revision record
        rev = Revision(section_id=sec.id, version=version, content=final_content, score=score)
        db.add(rev)
        db.commit()
        db.refresh(sec)

        generated[sec.title] = final_content

    return {"generated": generated}


@router.get("/{project_id}/export")
def export_project(project_id: int, type: Optional[str] = Query("docx", regex="^(docx|pptx)$"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Export the project to DOCX or PPTX and return file path (FileResponse).
    """
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sections = db.query(Section).filter(Section.project_id == project_id).order_by(Section.id).all()
    content_map = {s.title: s.content or "" for s in sections}

    if type == "docx":
        path = export_to_docx(project.title, content_map)
    else:
        path = export_to_pptx(project.title, content_map)

    return FileResponse(path, filename=path.split("/")[-1])
