# syntax=docker/dockerfile:1.7
# qubit-notes: the API and the built frontend, served by uvicorn on port 8000.
#
# gogi-python, which the backend installs from ../../gogi-python, comes in as a build context of its own:
#
#   docker build --build-context gogi-python=../gogi-python -t qubit-notes .
#
# Run it with its settings, e.g. QUBIT_NOTES_DATABASE_URL, QUBIT_NOTES_GATEWAY_URL and QUBIT_NOTES_GOGI_API_KEY; it
# migrates its database when it starts.

FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY frontend/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:0.8.22-python3.12-bookworm-slim AS backend
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
# the backend's path source, ../../gogi-python, from /app/backend
COPY --from=gogi-python . /gogi-python
# gogi-python's protobuf code is generated, not kept in its repository
RUN --mount=type=cache,target=/root/.cache/uv \
    cd /gogi-python && rm -rf .venv && uv run --frozen python scripts/build_protos.py
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-project
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm
RUN useradd --system --uid 10001 --home-dir /app qubit
WORKDIR /app
# without QUBIT_NOTES_DATABASE_URL, the app keeps its data in SQLite here
RUN chown qubit /app
COPY --from=backend --chown=qubit /app/backend/.venv /app/backend/.venv
COPY --from=frontend --chown=qubit /app/frontend/dist /app/frontend
ENV PATH=/app/backend/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    QUBIT_NOTES_FRONTEND_DIR=/app/frontend
USER qubit
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/config', timeout=4)"
# behind a TLS proxy, e.g. Caddy or CloudFront, which says who the client is
CMD ["uvicorn", "qubit_notes.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
