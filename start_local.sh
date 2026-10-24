#!/usr/bin/env bash
# Runs qubit-notes locally, on its own platform, against the dev database.
#
#   ./start_local.sh          # build the frontend and serve it with the API on http://localhost:8001
#   ./start_local.sh dev      # API on :8001 and the Vite dev server on http://localhost:5173, reloading on changes
#
# Settings come from the environment and from .env beside this script (gitignored), whose values win, e.g.
#   QUBIT_NOTES_ANTHROPIC_API_KEY=sk-ant-...
# It makes the app's secret (QUBIT_NOTES_SECRET_KEY) into .env the first time, and makes whoever runs it the app's
# admin (QUBIT_NOTES_ADMINS=$USER), who can give the app a key it is missing from the platform's status.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-serve}"
CONTAINER=qubit-notes-pgvector

if [[ "$MODE" != serve && "$MODE" != dev ]]; then
    echo "usage: $0 [serve|dev]" >&2
    exit 2
fi

if [[ -f "$ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT/.env"
    set +a
fi

# what the keys an admin gives the app are encrypted with: made once, and kept in .env
if [[ -z "${QUBIT_NOTES_SECRET_KEY:-}" ]]; then
    QUBIT_NOTES_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    # .env may not end with a new line
    [[ -s "$ROOT/.env" && -n "$(tail -c1 "$ROOT/.env")" ]] && echo >>"$ROOT/.env"
    echo "QUBIT_NOTES_SECRET_KEY=$QUBIT_NOTES_SECRET_KEY" >>"$ROOT/.env"
    echo "made the app's secret, kept in .env"
fi
export QUBIT_NOTES_SECRET_KEY
# locally, whoever runs the app is its admin, and can give it the keys it is missing
export QUBIT_NOTES_ADMINS="${QUBIT_NOTES_ADMINS:-$USER}"

export QUBIT_NOTES_DATABASE_URL="${QUBIT_NOTES_DATABASE_URL:-postgresql+psycopg://qubit:qubit@127.0.0.1:5433/qubit_notes_dev}"
# keeps the in-app embedding model between restarts, rather than downloading it again
export QUBIT_NOTES_EMBEDDING_CACHE_DIR="${QUBIT_NOTES_EMBEDDING_CACHE_DIR:-$HOME/.cache/qubit-notes/models}"

UV="${UV:-$(command -v uv || echo "$HOME/anaconda3/envs/sa-3.12/bin/uv")}"
if [[ ! -x "$UV" ]]; then
    echo "uv not found; set UV=/path/to/uv" >&2
    exit 1
fi

# the dev database, where it's the local container
if [[ "$QUBIT_NOTES_DATABASE_URL" == *"127.0.0.1:5433"* ]]; then
    if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
        if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
            echo "starting $CONTAINER"
            docker start "$CONTAINER" >/dev/null
        else
            echo "no container $CONTAINER; start Postgres with pgvector on 127.0.0.1:5433, e.g." >&2
            echo "  docker run -d --name $CONTAINER -p 127.0.0.1:5433:5432 -e POSTGRES_USER=qubit" \
                "-e POSTGRES_PASSWORD=qubit -e POSTGRES_DB=qubit_notes_dev pgvector/pgvector:pg16" >&2
            exit 1
        fi
    fi
    until docker exec "$CONTAINER" pg_isready -U qubit -q; do sleep 1; done
fi

if [[ -z "${QUBIT_NOTES_ANTHROPIC_API_KEY:-}${QUBIT_NOTES_OPENAI_API_KEY:-}" ]]; then
    echo "warning: no QUBIT_NOTES_ANTHROPIC_API_KEY in the settings; unless $QUBIT_NOTES_ADMINS gave the app one" \
        "(sign in as $QUBIT_NOTES_ADMINS and open the platform's status), the AI won't work" >&2
fi

# keeps the test tools (make install) and gogi-python (make install-gogi), which a plain sync would remove
(cd "$ROOT/backend" && "$UV" sync -q --extra dev --inexact && "$UV" run qubit-notes migrate)
[[ -d "$ROOT/frontend/node_modules" ]] || (cd "$ROOT/frontend" && npm install)

cd "$ROOT"
if [[ "$MODE" == serve ]]; then
    exec make UV="$UV" serve
fi

make UV="$UV" dev-backend &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null; wait "$BACKEND_PID" 2>/dev/null' EXIT
make dev-frontend
