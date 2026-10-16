# Study Assistant

A study assistant built on the [gogi](../gogi) platform with the [gogi-python](../gogi-python) SDK. Students upload
their study material, ask questions about it, and get answers that cite their sources. The assistant also keeps
study sessions with memory, generates quizzes and flashcards, and schedules reviews.

- `backend/`: FastAPI app. The domain talks to gogi only through the `StudyPlatform` port
  (`backend/src/study_assistant/platform/port.py`). `GogiPlatform` implements the port with the SDK.
- `frontend/`: React + TypeScript (Vite).
- `features/`: Gherkin specs. They drive development of both the backend and the UI.

## Behaviour-driven development

Each capability starts as a `.feature` file in `features/`. Its steps live in `backend/tests/bdd/steps/`.

- `make bdd` runs every scenario against `FakePlatform`, an in-memory platform. It needs no gogi stack and no API
  keys.
- `make bdd-gogi` runs only the scenarios tagged `@gogi`, against a running gogi gateway
  (`STUDY_ASSISTANT_GATEWAY_URL`, default `localhost:50051`). When one of these fails because of the platform, the
  fix goes into gogi or gogi-python.

## Development

```bash
make install            # backend venv (uv) and frontend packages
make dev-backend        # http://localhost:8001/api/health (gogi's chromadb takes 8000)
make dev-frontend       # http://localhost:5173, forwards /api to the backend
make lint
```

The backend needs Python 3.12+ and installs gogi-python from `../../gogi-python` in editable mode. Build its
protobuf code first (`gogi-python/install.sh` or `uv run python scripts/build_protos.py`).
