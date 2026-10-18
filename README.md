# Study Assistant

A study assistant built on the [gogi](../gogi) platform with the [gogi-python](../gogi-python) SDK. Students upload
their study material, ask questions about it, and get answers that cite their sources. The assistant also keeps
study sessions with memory, generates quizzes and flashcards, and schedules reviews.

- `backend/`: FastAPI app. The domain talks to gogi only through the `StudyPlatform` port
  (`backend/src/study_assistant/platform/port.py`). `GogiPlatform` implements the port with the SDK.
- `frontend/`: React + TypeScript (Vite). Students sign in by name (there is no authentication yet), manage their
  courses' material by subject and topic, and share courses with classmates.
- `features/`: Gherkin specs. They drive development of both the backend and the UI.

## Behaviour-driven development

Each capability starts as a `.feature` file in `features/`. Its steps live in `backend/tests/bdd/steps/`.

- `make bdd` runs every scenario against `FakePlatform`, an in-memory platform. It needs no gogi stack and no API
  keys. Scenarios tagged `@ui` build the frontend, serve it from the backend and drive it in headless Chromium with
  Playwright. `make bdd-ui` runs only those.
- `make bdd-gogi` runs only the scenarios tagged `@gogi`, against a running gogi gateway
  (`STUDY_ASSISTANT_GATEWAY_URL`, default `localhost:50051`). When one of these fails because of the platform, the
  fix goes into gogi or gogi-python.

## Development

```bash
make install            # backend venv (uv), Playwright's Chromium and frontend packages
make serve              # build the frontend and serve it with the backend on http://localhost:8001
make dev-backend        # http://localhost:8001/api/health (gogi's chromadb takes 8000)
make dev-frontend       # http://localhost:5173, forwards /api to the backend
make lint
```

The backend needs Python 3.12+ and installs gogi-python from `../../gogi-python` in editable mode. Build its
protobuf code first (`gogi-python/install.sh` or `uv run python scripts/build_protos.py`).

## Running on a gogi that serves many applications

Where gogi serves many applications, gogi's operator registers the app (`gogi-admin register qubit-notes`) and gives
it a key. Run the app with it, and store the app's Anthropic key in gogi once, as the app's own:

```bash
export STUDY_ASSISTANT_GATEWAY_URL=gogi.example.org:443
export STUDY_ASSISTANT_GOGI_API_KEY=gogi_...
export STUDY_ASSISTANT_GOGI_CA_FILE=/etc/qubit-notes/gogi-ca.pem   # only where gogi has a certificate authority of its own
echo "$ANTHROPIC_API_KEY" | uv run study-assistant store-provider-key anthropic
```

`/api/health` reports the app as degraded if gogi does not take its key. Against a gogi without keys, as in
development, none of this is needed. The `@gogi` scenarios of `features/gogi_application.feature` run through gogi's
gateway that requires keys (`localhost:50050`), registering applications with `docker exec gogi-gateway-applications
/root/gogi-admin`.

## Contributing and releases

Pull requests are squash-merged, and the squash commit takes the PR's title as its message. So the title must be a
[conventional commit](https://www.conventionalcommits.org/): `feat: delete a course`,
`fix(reader): keep the section on reload`, `docs: …`, `ci: …`. The `PR title` check enforces it. Commits inside a PR
can be anything, since they are squashed away.

- **CI** (`.github/workflows/ci.yml`) runs on every PR and on `main`: ruff, ESLint and TypeScript, then every
  scenario on the in-memory platform, the `@ui` ones in Chromium. It checks out gogi-python's `main` next to this
  repository; to test against another gogi-python branch, run the workflow by hand with `gogi-python-ref`. The
  `@gogi` scenarios need a gogi stack, so they run locally only (`make bdd-gogi`).
- **Releases** (`.github/workflows/release.yml`): release-please keeps a release PR open with the next version and
  `CHANGELOG.md`, from the `feat` and `fix` commits on `main`. Merging it tags `vX.Y.Z` and publishes a GitHub
  release. The version is kept in `backend/pyproject.toml` and `frontend/package.json`. Before 1.0, a `feat` bumps
  the minor version, as does a breaking change (`feat!: …`).
