# Qubit Notes

Qubit Notes is a study app. Students upload their study material, ask questions about it, and get answers that cite
their sources. The assistant also keeps study sessions with memory, generates quizzes and flashcards, and schedules
reviews.

The app needs nothing but its own database, a place for files and a model provider: by default it is its own
platform. It can run on the [gogi](../gogi) platform instead, with the [gogi-python](../gogi-python) SDK.

- `backend/`: FastAPI app. The domain talks to its platform only through the `StudyPlatform` port
  (`backend/src/qubit_notes/platform/port.py`). `StandalonePlatform` (`platform/standalone/`) implements it with the
  app's own database, files and model providers; `GogiPlatform` implements it with gogi-python.
- `frontend/`: React + TypeScript (Vite). Students sign in by name (there is no authentication yet), manage their
  courses' material by subject and topic, and share courses with classmates.
- `features/`: Gherkin specs. They drive development of both the backend and the UI.

## Behaviour-driven development

Each capability starts as a `.feature` file in `features/`. Its steps live in `backend/tests/bdd/steps/`.

- `make bdd` runs every scenario against `FakePlatform`, an in-memory platform. It needs no gogi stack and no API
  keys. Scenarios tagged `@ui` build the frontend, serve it from the backend and drive it in headless Chromium with
  Playwright. `make bdd-ui` runs only those.
- `make bdd-standalone` runs the scenarios tagged `@platform` or `@standalone` against the app's own platform: its
  database (SQLite, or `QUBIT_NOTES_TEST_DATABASE_URL`), files in a temporary directory, and its in-app embedding
  models, downloaded the first time. The AI is a stand-in; `make bdd-standalone-ai` uses Anthropic's
  (`QUBIT_NOTES_ANTHROPIC_API_KEY`). `--with-embedding-keys` also runs the scenarios that embed with Voyage AI and
  OpenAI.
- `make bdd-gogi` runs only the scenarios tagged `@platform`, against a running gogi gateway
  (`QUBIT_NOTES_GATEWAY_URL`, default `localhost:50051`); it needs gogi-python (`make install-gogi`).

## Development

```bash
make install            # backend venv (uv), Playwright's Chromium and frontend packages
make serve              # build the frontend and serve it with the backend on http://localhost:8001
make dev-backend        # http://localhost:8001/api/health (gogi's chromadb takes 8000)
make dev-frontend       # http://localhost:5173, forwards /api to the backend
make lint
```

`./start_local.sh` does it all in one go, on the app's own platform: it reads settings such as
`QUBIT_NOTES_ANTHROPIC_API_KEY` from `.env` (gitignored) if there is one, uses the dev database (Postgres with
pgvector in the container `qubit-notes-pgvector`, on `127.0.0.1:5433`) unless `QUBIT_NOTES_DATABASE_URL` is set,
starts that container if it's stopped, runs the migrations and then `make serve`; `./start_local.sh dev` runs
`make dev-backend` and `make dev-frontend` together instead.

The backend needs Python 3.12+. To run the app on gogi, `make install-gogi` also installs gogi-python from
`../gogi-python` in editable mode; build its protobuf code first (`gogi-python/install.sh` or
`uv run python scripts/build_protos.py`). gogi-python isn't one of the app's dependencies, so a plain `uv sync`
removes it again; `uv run` leaves it.

## The app's database

The app keeps what students make (notes, summaries, quizzes, conversations, topics) in its own database:
SQLite by default (`backend/qubit-notes.db`), Postgres where it's deployed:

```bash
export QUBIT_NOTES_DATABASE_URL=postgresql+psycopg://qubit:...@db.example.org:5432/qubit_notes
uv run qubit-notes migrate      # a deployment runs it before the new version serves; the app also migrates when it starts
```

The tables are made and changed by the Alembic migrations in `backend/src/qubit_notes/migrations/versions`. A change
to `storage.py` needs one: from `backend/`, `uv run alembic revision --autogenerate -m "..."`, then check what it
wrote. `tests/unit/test_migrations.py` fails if `storage.py` and the migrations differ; with
`QUBIT_NOTES_TEST_POSTGRES_URL` set it checks Postgres too, and `QUBIT_NOTES_TEST_DATABASE_URL` runs the scenarios
against a database of your choosing, as CI does with Postgres.

## PDFs and EPUBs

An uploaded PDF or EPUB is converted to Markdown in the background (`features/converting.feature`,
`backend/src/qubit_notes/conversion/`), and from then on the material is that Markdown: students read, edit, search,
summarise and quiz it as Markdown. Its pictures become its images.

- PDFs are converted with [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) (AGPL, as is PyMuPDF): headings from
  the PDF's outline if it has one, else from its font sizes, else a section per page. A PDF without text, such as a
  scan, fails with a message saying so; there is no OCR.
- EPUBs are converted with ebooklib and markdownify: a chapter's headings, or its title in the table of contents.
- Two downloads: the original file, unchanged, and the material as it is now, as a PDF or an EPUB laid out anew
  from its Markdown (with PyMuPDF and ebooklib), with an outline of its headings or a chapter per top heading.

The platform keeps a converted material's Markdown as `<name>.md`, so gogi reads it as Markdown too; the app shows it
by the name it was uploaded with (`platform/named.py`). PDFs uploaded before this stay as they were: read, but not
edited.

## The app's own platform

By default (`QUBIT_NOTES_PLATFORM=standalone`) the app is its own platform (`features/standalone.feature`):

- **Material.** Uploads are kept in a directory (`QUBIT_NOTES_FILES_DIR`, `backend/material` by default) or an S3
  bucket (`QUBIT_NOTES_FILES_BUCKET`). In the background, each document is read into its sections (a Markdown file
  by its headings, a PDF by its outline or else page by page), divided into chunks and embedded. Courses, documents,
  sections and chunks are kept in the app's database, the `platform_*` tables.
- **Search.** On Postgres, with pgvector, which the migrations turn on (Amazon RDS has it; locally, use the
  `pgvector/pgvector:pg16` image). On SQLite, in Python.
- **Embedding models** (`QUBIT_NOTES_EMBEDDING_MODEL`): `bge-small-en-v1.5` (the default) and `all-minilm-l6-v2` run
  in the app and need no key; `voyage-*` models, e.g. `voyage-3.5-lite`, need `QUBIT_NOTES_VOYAGE_API_KEY`;
  `text-embedding-3-*` models need `QUBIT_NOTES_OPENAI_API_KEY`. Material embedded with one model is found only by
  searching with the same model: after changing it, run `qubit-notes reembed`.
- **The AI** (`QUBIT_NOTES_LLM_PROVIDER`, `QUBIT_NOTES_LLM_MODEL`): Anthropic's models with
  `QUBIT_NOTES_ANTHROPIC_API_KEY` (the default), or OpenAI's with `QUBIT_NOTES_OPENAI_API_KEY`. Conversations and what
  the assistant remembers are kept in the app's database.

```bash
export QUBIT_NOTES_ANTHROPIC_API_KEY=sk-ant-...
make dev-backend
```

`/api/health` reports the app's database, files, embeddings and AI, and reports it degraded without the key of its
model provider. Unfinished ingestions are resumed when the app starts again, so run one replica of the app.

## Running on a gogi that serves many applications

Set `QUBIT_NOTES_PLATFORM=gogi`, and install gogi-python beside the app (`make install-gogi`, or build the image
with it, below).

Where gogi serves many applications, gogi's operator registers the app (`gogi-admin register qubit-notes`) and gives
it a key. Run the app with it, and store the app's Anthropic key in gogi once, as the app's own:

```bash
export QUBIT_NOTES_GATEWAY_URL=gogi.example.org:443
export QUBIT_NOTES_GOGI_API_KEY=gogi_...
export QUBIT_NOTES_GOGI_CA_FILE=/etc/qubit-notes/gogi-ca.pem   # only where gogi has a certificate authority of its own
echo "$ANTHROPIC_API_KEY" | uv run qubit-notes store-provider-key anthropic
```

`/api/health` reports the app as degraded if gogi does not take its key. Against a gogi without keys, as in
development, none of this is needed. The scenarios of `features/gogi_application.feature` run through gogi's
gateway that requires keys (`localhost:50050`), registering applications with `docker exec gogi-gateway-applications
/root/gogi-admin`.

## Signing in with Amazon Cognito

Where the app is deployed, students sign in with Amazon Cognito rather than by name
(`features/sign_in.feature`, `features/ui_sign_in.feature`). The user pool needs an app client that is public (no
client secret), with the authorization code grant, the `openid` scope, and the app's address, e.g.
`https://notes.example.org/`, as both its callback and its sign-out URL; and a domain for its sign-in pages.

```bash
export QUBIT_NOTES_AUTH=cognito
export QUBIT_NOTES_COGNITO_REGION=eu-west-2
export QUBIT_NOTES_COGNITO_USER_POOL_ID=eu-west-2_AbC123
export QUBIT_NOTES_COGNITO_CLIENT_ID=...
export QUBIT_NOTES_COGNITO_DOMAIN=https://qubit-notes.auth.eu-west-2.amazoncognito.com
```

The browser signs in with PKCE and sends the access token with every request; the backend checks it against the
pool's keys, issuer, app client and expiry, and the student is the token's username. A video's link carries the token
(`?access_token=`), as a `<video>` can't send headers. The tests stand in for Cognito with
`backend/tests/fakes/fake_cognito.py`.

## The container image

One image serves the API and the built frontend on port 8000, on the app's own platform, with its default embedding
model in it:

```bash
docker build -t qubit-notes .
docker run -p 8000:8000 -e QUBIT_NOTES_DATABASE_URL=postgresql+psycopg://... -e QUBIT_NOTES_FILES_BUCKET=... \
  -e QUBIT_NOTES_ANTHROPIC_API_KEY=... qubit-notes
```

Without a bucket, uploads are kept in `/app/material`, which wants a volume. To run the image on gogi, build it with
gogi-python, which comes in as a build context of its own:
`docker build --build-arg BACKEND=backend-gogi --build-context gogi-python=../gogi-python -t qubit-notes .`

It runs as a non-root user, migrates its database when it starts, and is healthy once `/api/config` answers. CI builds
it for every PR and pushes `ghcr.io/pockerman/qubit-notes:main` from main; a release pushes `:<version>` and `:latest`.

## Deploying on AWS

[`deploy/aws`](deploy/aws) is the Terraform for the app on AWS, on its own platform, or, with `platform = "gogi"`, as
one of the applications of a gogi deployment (gogi's `docs/deployment.md`):

| | |
|---|---|
| Address | CloudFront, at `https://<id>.cloudfront.net` while there's no domain; it reaches the server privately, through a VPC origin |
| Server | one EC2 instance (`t3.small`), Amazon Linux 2023, running the image as `qubit-notes.service`; reached with SSM Session Manager, not SSH |
| Sign-in | a Cognito user pool, with its own sign-in pages at an `amazoncognito.com` address |
| Data | RDS for PostgreSQL 16 (`db.t4g.micro`) with pgvector, in private subnets, backed up for a week |
| Files | an S3 bucket of the students' uploads, private, reached through a gateway endpoint; replaced or deleted uploads are kept 30 days |
| Secrets | Secrets Manager: the database's password, and the app's keys of the model providers |

This costs about $40 a month in eu-west-2 at on-demand prices. The server keeps nothing of its own, so it can be
replaced at any time.

1. Keep the state somewhere private, as it holds the database's password: copy `backend.tf.example` to
   `backend.tf` and name an S3 bucket of your own. Then apply:

   ```bash
   cd deploy/aws
   terraform init
   terraform apply
   ```

2. Put the app's keys of the model providers where its server reads them: Anthropic's, and Voyage AI's or OpenAI's if
   the embedding model is one of theirs (`app_settings = { QUBIT_NOTES_EMBEDDING_MODEL = "voyage-3.5-lite" }`). If
   the image is private, put a token that can read it in `qubit-notes/registry` too, as
   `{"username": "...", "token": "..."}`.

   ```bash
   read -rs ANTHROPIC_API_KEY
   aws secretsmanager put-secret-value --secret-id "$(terraform output -raw provider_keys_secret)" \
     --secret-string "$(jq -n --arg key "$ANTHROPIC_API_KEY" '{anthropic: $key}')"
   ```

3. Restart the app on its server, so it reads them:

   ```bash
   aws ssm start-session --target "$(terraform output -raw instance_id)"
   sudo systemctl restart qubit-notes
   ```

4. Make the students' accounts; Cognito emails each their temporary password:

   ```bash
   aws cognito-idp admin-create-user --user-pool-id "$(terraform output -raw user_pool_id)" \
     --username maria --user-attributes Name=email,Value=maria@example.org Name=email_verified,Value=true
   ```

Then open `terraform output -raw url`. To run another image, set `image_tag`, apply, and restart the app; the app's
other settings go in `app_settings`, e.g. `{ QUBIT_NOTES_LLM_MODEL = "..." }`. After changing the embedding model,
embed the material again on the server: `sudo docker exec qubit-notes qubit-notes reembed`.

### On gogi

With `platform = "gogi"` the app keeps no files or keys of its own, and uses an image built with gogi-python (above):

1. Deploy gogi first, and give the app gogi's address and certificate authority, e.g. in `terraform.tfvars`:

   ```hcl
   platform            = "gogi"
   gogi_gateway_url    = "203.0.113.9:443"   # gogi's gateway_address output
   gogi_ca_certificate = file("gogi-ca.pem")  # gogi's ca_certificate output
   ```

2. Let the app's server into gogi: add `terraform output -raw server_public_ip`, as `<ip>/32`, to gogi's
   `client_cidrs`, and apply gogi.
3. Register the app with gogi (`gogi-admin register qubit-notes` on gogi's server), and put its key in
   `terraform output -raw gogi_api_key_secret`.
4. On the app's server, restart the app and store its Anthropic key in gogi:

   ```bash
   sudo systemctl restart qubit-notes
   read -rs ANTHROPIC_API_KEY && echo "$ANTHROPIC_API_KEY" | sudo docker exec -i qubit-notes qubit-notes store-provider-key anthropic
   ```

## Contributing and releases

Pull requests are squash-merged, and the squash commit takes the PR's title as its message. So the title must be a
[conventional commit](https://www.conventionalcommits.org/): `feat: delete a course`,
`fix(reader): keep the section on reload`, `docs: …`, `ci: …`. The `PR title` check enforces it. Commits inside a PR
can be anything, since they are squashed away.

- **CI** (`.github/workflows/ci.yml`) runs on every PR and on `main`: ruff, ESLint and TypeScript, then every
  scenario on the in-memory platform, the `@ui` ones in Chromium, and the `@platform` and `@standalone` ones on the
  app's own platform, with Postgres and pgvector. It needs nothing but this repository. Runs on gogi need a gogi
  stack, so they run locally only (`make bdd-gogi`).
- **Releases** (`.github/workflows/release.yml`): release-please keeps a release PR open with the next version and
  `CHANGELOG.md`, from the `feat` and `fix` commits on `main`. Merging it tags `vX.Y.Z` and publishes a GitHub
  release. The version is kept in `backend/pyproject.toml` and `frontend/package.json`. Before 1.0, a `feat` bumps
  the minor version, as does a breaking change (`feat!: …`).
