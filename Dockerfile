# syntax=docker/dockerfile:1

ARG NODE_VERSION=22-alpine
ARG PYTHON_VERSION=3.11-slim

FROM node:${NODE_VERSION} AS frontend-build
WORKDIR /app/frontend

# Install frontend dependencies and build the static bundle
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:${PYTHON_VERSION} AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies required for psycopg2 and other native wheels
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install backend Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy the built frontend assets into the backend so FastAPI can serve them
RUN mkdir -p backend/app/static
COPY --from=frontend-build /app/frontend/dist/ ./backend/app/static/

WORKDIR /app/backend

EXPOSE 8000
ENV PORT=8000

# Allow overriding uvicorn workers via CMD arguments if needed
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
