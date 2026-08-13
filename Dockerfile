# syntax=docker/dockerfile:1
#
# Container for Hugging Face Spaces (Docker SDK) — and any other Docker host.
# Two stages: build the React SPA with Node, then serve everything (UI + the
# streaming API) from Python/uvicorn on a single port. See the "Deploy to
# Hugging Face Spaces" section of README.md.

# ---------- Stage 1: build the React + Vite SPA ----------
FROM node:20-slim AS frontend
WORKDIR /app/web/frontend

# Install from a clean lockfile. A fresh Linux install sidesteps the
# @rollup/rollup-<platform> optional-dependency mismatch you hit if node_modules
# was ever populated on macOS.
COPY web/frontend/package.json web/frontend/package-lock.json ./
RUN npm ci

COPY web/frontend/ ./
RUN npm run build          # emits /app/web/frontend/dist

# ---------- Stage 2: Python runtime ----------
FROM python:3.11-slim AS runtime

# Hugging Face Spaces best practice: run as a non-root user (uid 1000).
RUN useradd --create-home --uid 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

WORKDIR /home/user/app

# Python deps first for better layer caching (app code changes more often).
# requirements-otel.txt is included so a host can turn on trace export purely by
# setting OTEL_* env vars; observability.py stays inert until an endpoint is set,
# but without the exporter package installed it can only print a "not installed"
# hint and give up.
COPY --chown=user:user requirements.txt ./requirements.txt
COPY --chown=user:user web/requirements.txt ./web/requirements.txt
COPY --chown=user:user requirements-otel.txt ./requirements-otel.txt
RUN pip install --no-cache-dir \
    -r requirements.txt -r web/requirements.txt -r requirements-otel.txt

# App source. .dockerignore keeps out .env, node_modules, the local dist, and
# the gitignored private/ playbooks — so no secrets or internal content are baked
# into the image.
COPY --chown=user:user gtm_agent ./gtm_agent
COPY --chown=user:user web ./web

# Built SPA from stage 1 (creates web/frontend/dist, which server.py prefers).
COPY --chown=user:user --from=frontend /app/web/frontend/dist ./web/frontend/dist

USER user
EXPOSE 7860

# HF routes to app_port (README front-matter = 7860). Honor $PORT if the host
# sets one; default to 7860 otherwise.
CMD ["sh", "-c", "uvicorn web.server:app --host 0.0.0.0 --port ${PORT:-7860}"]
