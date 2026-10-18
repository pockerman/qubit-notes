# Qubit Notes

Qubit Notes is a study app built on the [gogi](../gogi) platform with the [gogi-python](../gogi-python) SDK. Students upload
their study material, ask questions about it, and get answers that cite their sources. The assistant also keeps
study sessions with memory, generates quizzes and flashcards, and schedules reviews.

- `backend/`: FastAPI app. The domain talks to gogi only through the `StudyPlatform` port
  (`backend/src/qubit_notes/platform/port.py`). `GogiPlatform` implements the port with the SDK.
- `frontend/`: React + TypeScript (Vite). Students sign in by name (there is no authentication yet), manage their
  courses' material by subject and topic, and share courses with classmates.
- `features/`: Gherkin specs. They drive development of both the backend and the UI.

## Behaviour-driven development

Each capability starts as a `.feature` file in `features/`. Its steps live in `backend/tests/bdd/steps/`.

- `make bdd` runs every scenario against `FakePlatform`, an in-memory platform. It needs no gogi stack and no API
  keys. Scenarios tagged `@ui` build the frontend, serve it from the backend and drive it in headless Chromium with
  Playwright. `make bdd-ui` runs only those.
- `make bdd-gogi` runs only the scenarios tagged `@gogi`, against a running gogi gateway
  (`QUBIT_NOTES_GATEWAY_URL`, default `localhost:50051`). When one of these fails because of the platform, the
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

## Running on a gogi that serves many applications

Where gogi serves many applications, gogi's operator registers the app (`gogi-admin register qubit-notes`) and gives
it a key. Run the app with it, and store the app's Anthropic key in gogi once, as the app's own:

```bash
export QUBIT_NOTES_GATEWAY_URL=gogi.example.org:443
export QUBIT_NOTES_GOGI_API_KEY=gogi_...
export QUBIT_NOTES_GOGI_CA_FILE=/etc/qubit-notes/gogi-ca.pem   # only where gogi has a certificate authority of its own
echo "$ANTHROPIC_API_KEY" | uv run qubit-notes store-provider-key anthropic
```

`/api/health` reports the app as degraded if gogi does not take its key. Against a gogi without keys, as in
development, none of this is needed. The `@gogi` scenarios of `features/gogi_application.feature` run through gogi's
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

One image serves the API and the built frontend on port 8000. gogi-python comes in as a build context of its own:

```bash
docker build --build-context gogi-python=../gogi-python -t qubit-notes .
docker run -p 8000:8000 -e QUBIT_NOTES_DATABASE_URL=postgresql+psycopg://... -e QUBIT_NOTES_GATEWAY_URL=... qubit-notes
```

It runs as a non-root user, migrates its database when it starts, and is healthy once `/api/config` answers. CI builds
it for every PR and pushes `ghcr.io/pockerman/qubit-notes:main` from main; a release pushes `:<version>` and `:latest`.

## Deploying on AWS

[`deploy/aws`](deploy/aws) is the Terraform for the app on AWS, as one of the applications of a gogi deployment
(gogi's `docs/deployment.md`):

| | |
|---|---|
| Address | CloudFront, at `https://<id>.cloudfront.net` while there's no domain; it reaches the server privately, through a VPC origin |
| Server | one EC2 instance (`t3.small`), Amazon Linux 2023, running the image as `qubit-notes.service`; reached with SSM Session Manager, not SSH |
| Sign-in | a Cognito user pool, with its own sign-in pages at an `amazoncognito.com` address |
| Data | RDS for PostgreSQL 16 (`db.t4g.micro`), in private subnets, backed up for a week; the materials' files are kept in gogi |
| Secrets | Secrets Manager: the database's password, and the key gogi gave the app |

This costs about $40 a month in eu-west-2 at on-demand prices. The server keeps nothing of its own, so it can be
replaced at any time.

1. Deploy gogi first. Keep this state somewhere private too, as it holds the database's password: copy
   `backend.tf.example` to `backend.tf` and name an S3 bucket of your own.
2. Give the app gogi's address and certificate authority, e.g. in `terraform.tfvars`, and apply:

   ```hcl
   gogi_gateway_url    = "203.0.113.9:443"   # gogi's gateway_address output
   gogi_ca_certificate = file("gogi-ca.pem")  # gogi's ca_certificate output
   ```

   ```bash
   cd deploy/aws
   terraform init
   terraform apply
   ```

3. Let the app's server into gogi: add `terraform output -raw server_public_ip`, as `<ip>/32`, to gogi's
   `client_cidrs`, and apply gogi.
4. Register the app with gogi (`gogi-admin register qubit-notes` on gogi's server), and put its key where the app's
   server reads it. If the image is private, put a token that can read it in `qubit-notes/registry` too, as
   `{"username": "...", "token": "..."}`.

   ```bash
   aws secretsmanager put-secret-value --secret-id qubit-notes/gogi-api-key --secret-string 'gogi_...'
   ```

5. On the app's server, restart the app and store its Anthropic key in gogi:

   ```bash
   aws ssm start-session --target "$(terraform output -raw instance_id)"
   sudo systemctl restart qubit-notes
   read -rs ANTHROPIC_API_KEY && echo "$ANTHROPIC_API_KEY" | sudo docker exec -i qubit-notes qubit-notes store-provider-key anthropic
   ```

6. Make the students' accounts; Cognito emails each their temporary password:

   ```bash
   aws cognito-idp admin-create-user --user-pool-id "$(terraform output -raw user_pool_id)" \
     --username maria --user-attributes Name=email,Value=maria@example.org Name=email_verified,Value=true
   ```

Then open `terraform output -raw url`. To run another image, set `image_tag`, apply, and restart the app; the app's
other settings go in `app_settings`, e.g. `{ QUBIT_NOTES_LLM_MODEL = "..." }`.

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
