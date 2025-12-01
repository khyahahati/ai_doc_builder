docker build -t ai-doc-builder .
# AI Document Builder

A lightweight document automation stack that pairs a FastAPI backend with a Vite + React SPA. It helps product teams draft outlines, generate section content with Google Generative AI, iterate with feedback, and export polished docs.

---

## Project Overview

* Create workspaces backed by a relational data model
* Draft document outlines and store revisions in SQLite (or Postgres)
* Invoke LangGraph workflows to generate and refine section content using Gemini
* Collaborate through a React-based workspace with inline feedback
* Export finished projects as DOCX or PPTX assets

---

## Technologies & Tools Used

| Tool | Description |
| --- | --- |
| ![](https://img.shields.io/badge/-Python%203.11-3776AB?logo=python&logoColor=white&style=flat-square) | Language powering the backend services |
| ![](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white&style=flat-square) | REST API framework with automatic OpenAPI docs |
| ![](https://img.shields.io/badge/-React%20%2B%20Vite-61DAFB?logo=react&logoColor=white&style=flat-square) | Frontend SPA and dev tooling |
| ![](https://img.shields.io/badge/-LangGraph-5A4EE5?style=flat-square) | Workflow engine orchestrating LLM steps |
| ![](https://img.shields.io/badge/-Google%20Generative%20AI-4285F4?logo=google&logoColor=white&style=flat-square) | Gemini models for content generation |
| ![](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white&style=flat-square) | Default relational store (swap for Postgres if needed) |
| ![](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat-square) | Container packaging for local or hosted runs |

---

## How the Builder Works

### FastAPI Backend

* Organizes auth, projects, and sections into modular routers under `backend/app`
* Uses SQLAlchemy models plus migrations-ready schemas to persist data
* Serves static SPA assets and exposes auto-generated docs at `/docs`

### AI Workflow Orchestration

* LangGraph stitches together generation, evaluation, and refinement nodes (`backend/app/workflows`)
* Google Generative AI (Gemini) powers outline refinement and section drafting through `llm_service`
* Feedback flows (`like`, `dislike`, `generate`) decide when to persist revisions or loop for quality

### Frontend Workspace

* React SPA (Vite) provides outline editing, section feedback, and export actions under `frontend/src`
* Persists authenticated sessions, calls backend REST APIs, and streams progress indicators
* Falls back to local draft generation if API tokens are missing

### Export & History

* Revision records (`Revision` model) capture each generated version for traceability
* Export service can render DOCX or PPTX packages from stored sections
* Simple SQLite DB by default; set `DATABASE_URL` to switch to Postgres

---

## Setup & Usage

### 1. Clone the Repository

```powershell
git clone https://github.com/<your-username>/ai_doc_builder.git
cd ai_doc_builder
```

### 2. Configure Environment Variables

```powershell
echo GENAI_API_KEY=sk-your-api-key > backend/.env
```

* Required: `GENAI_API_KEY` (Google Generative AI key)
* Optional: `DATABASE_URL` for Postgres (e.g. `postgresql+psycopg2://user:pass@host:5432/db`)

### 3. Run the Backend (FastAPI)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt
python init_db.py  # optional; tables auto-create on first run
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* API documentation: `http://127.0.0.1:8000/docs`
* Health/root endpoint: `http://127.0.0.1:8000/`

### 4. Run the Frontend (Vite + React)

```powershell
cd ../frontend
npm install
npm run dev
```

* Vite dev server: `http://localhost:5173`
* Configure API base URL in `frontend/src/api.js` if running backend elsewhere

### 5. Build & Run with Docker (optional)

```powershell
cd ..
docker build -t ai-doc-builder .
docker run -p 8000:8000 -e GENAI_API_KEY=sk-your-api-key ai-doc-builder
```

* Mount a host directory to `/app/backend` to persist the SQLite file across runs
* Container serves both API and compiled SPA at `http://localhost:8000`

---

## Testing the API (using cURL)

Replace placeholders like `<JWT_TOKEN>` and `<PROJECT_ID>` with real values.

### Register a User

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}'
```

### Login and Capture a Token

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=Passw0rd!"
```

Copy the `access_token` from the response and set it in your shell: `export TOKEN=<JWT_TOKEN>`.

### Create a Project

```bash
curl -X POST "http://127.0.0.1:8000/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Q4 Enablement Plan","doc_type":"docx"}'
```

### Submit an Outline

```bash
curl -X POST "http://127.0.0.1:8000/projects/<PROJECT_ID>/outline" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sections":["Overview","Key Initiatives","Next Steps"]}'
```

### Generate Section Content

```bash
curl -X POST "http://127.0.0.1:8000/projects/<PROJECT_ID>/generate" \
  -H "Authorization: Bearer $TOKEN"
```

### Refine a Section with Feedback

```bash
curl -X POST "http://127.0.0.1:8000/sections/<SECTION_ID>/refine" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feedback":"dislike","user_prompt":"Tighten the executive summary."}'
```

### Export the Project

```bash
curl -L "http://127.0.0.1:8000/projects/<PROJECT_ID>/export?type=docx" \
  -H "Authorization: Bearer $TOKEN" \
  -o ai-doc-builder.docx
```

---




