# uv is not always on PATH; override with e.g. make UV=~/anaconda3/envs/sa-3.12/bin/uv bdd
UV ?= uv
BACKEND := backend
FRONTEND := frontend

.PHONY: install bdd bdd-ui bdd-gogi lint serve dev-backend dev-frontend

install:
	cd $(BACKEND) && $(UV) sync --extra dev && $(UV) run playwright install chromium
	cd $(FRONTEND) && npm install

# every scenario, against the in-memory platform; the @ui ones build the frontend and drive it in Chromium
bdd:
	cd $(BACKEND) && $(UV) run pytest

# only the @ui scenarios
bdd-ui:
	cd $(BACKEND) && $(UV) run pytest -m ui

# the @gogi scenarios, against a running gogi stack (STUDY_ASSISTANT_GATEWAY_URL, default localhost:50051)
bdd-gogi:
	cd $(BACKEND) && $(UV) run pytest --platform=gogi

lint:
	cd $(BACKEND) && $(UV) run ruff check . && $(UV) run ruff format --check .
	cd $(FRONTEND) && npm run lint

# the built frontend served by the backend, as in production: http://localhost:8001
serve:
	cd $(FRONTEND) && npm run build
	cd $(BACKEND) && STUDY_ASSISTANT_FRONTEND_DIR=../$(FRONTEND)/dist $(UV) run uvicorn study_assistant.app:create_app --factory --port 8001

dev-backend:
	cd $(BACKEND) && $(UV) run uvicorn study_assistant.app:create_app --factory --reload --port 8001

dev-frontend:
	cd $(FRONTEND) && npm run dev
