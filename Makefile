# uv is not always on PATH; override with e.g. make UV=~/anaconda3/envs/sa-3.12/bin/uv bdd
UV ?= uv
BACKEND := backend
FRONTEND := frontend

.PHONY: install bdd bdd-gogi lint dev-backend dev-frontend

install:
	cd $(BACKEND) && $(UV) sync --extra dev
	cd $(FRONTEND) && npm install

# every scenario, against the in-memory platform
bdd:
	cd $(BACKEND) && $(UV) run pytest

# the @gogi scenarios, against a running gogi stack (STUDY_ASSISTANT_GATEWAY_URL, default localhost:50051)
bdd-gogi:
	cd $(BACKEND) && $(UV) run pytest --platform=gogi

lint:
	cd $(BACKEND) && $(UV) run ruff check . && $(UV) run ruff format --check .
	cd $(FRONTEND) && npm run lint

dev-backend:
	cd $(BACKEND) && $(UV) run uvicorn study_assistant.app:create_app --factory --reload --port 8001

dev-frontend:
	cd $(FRONTEND) && npm run dev
