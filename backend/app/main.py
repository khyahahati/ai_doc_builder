from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import auth, projects, sections

app = FastAPI(
    title="AI Document Builder",
    version="1.0.0",
)

FRONTEND_DIST = Path(__file__).resolve().parent / "static"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        # Serve built frontend assets when available (e.g., inside the Docker image)
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# ---- CORS (allow frontend access) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Initialize database ----
@app.on_event("startup")
def startup_event():
    init_db()


# ---- Root health endpoint ----
@app.get("/")
def root():
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Backend is running ✅"}


@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    if not FRONTEND_DIST.exists():
        raise HTTPException(status_code=404, detail="Not Found")

    direct_file = FRONTEND_DIST / path
    if direct_file.is_file():
        return FileResponse(direct_file)

    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    raise HTTPException(status_code=404, detail="Not Found")


# ---- Register routers ----
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sections.router)
