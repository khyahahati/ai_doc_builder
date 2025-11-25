from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import auth, projects, sections

app = FastAPI(
    title="AI Document Builder",
    version="1.0.0",
)

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
    return {"message": "Backend is running ✅"}


# ---- Register routers ----
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sections.router)
