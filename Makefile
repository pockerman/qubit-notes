# uv is not always on PATH; override with e.g. make UV=~/anaconda3/envs/sa-3.12/bin/uv bdd
UV ?= uv
BACKEND := backend
FRONTEND := frontend

.PHONY: install install-gogi bdd bdd-ui bdd-standalone bdd-standalone-ai bdd-gogi bdd-gogi-ai lint serve dev-backend dev-frontend

install:
	cd $(BACKEND) && $(UV) sync --extra dev && $(UV) run playwright install chromium
	cd $(FRONTEND) && npm install

# also gogi-python, from ../gogi-python, to run the app on gogi (QUBIT_NOTES_PLATFORM=gogi); it isn't one of the
# app's dependencies, so a plain uv sync removes it again (uv run leaves it)
install-gogi: install
	cd $(BACKEND) && $(UV) pip install -e ../../gogi-python

# every scenario, against the in-memory platform; the @ui ones build the frontend and drive it in Chromium
bdd:
	cd $(BACKEND) && $(UV) run pytest

# the @platform and @standalone scenarios, against the app's own platform, with a stand-in for the AI
bdd-standalone:
	cd $(BACKEND) && $(UV) run pytest --platform=standalone

# the same with the real AI: QUBIT_NOTES_ANTHROPIC_API_KEY
bdd-standalone-ai:
	cd $(BACKEND) && $(UV) run pytest --platform=standalone --with-ai

# only the @ui scenarios
bdd-ui:
	cd $(BACKEND) && $(UV) run pytest -m ui

# the @platform scenarios, against a running gogi stack (QUBIT_NOTES_GATEWAY_URL, default localhost:50051); needs
# make install-gogi
bdd-gogi:
	cd $(BACKEND) && $(UV) run pytest --platform=gogi

# the @platform scenarios including those that need the AI: gogi needs a model provider's API key
bdd-gogi-ai:
	cd $(BACKEND) && $(UV) run pytest --platform=gogi --with-ai

lint:
	cd $(BACKEND) && $(UV) run ruff check . && $(UV) run ruff format --check .
	cd $(FRONTEND) && npm run lint

# the built frontend served by the backend, as in production: http://localhost:8001
serve:
	cd $(FRONTEND) && npm run build
	cd $(BACKEND) && QUBIT_NOTES_FRONTEND_DIR=../$(FRONTEND)/dist $(UV) run uvicorn qubit_notes.app:create_app --factory --port 8001

dev-backend:
	cd $(BACKEND) && $(UV) run uvicorn qubit_notes.app:create_app --factory --reload --port 8001

dev-frontend:
	cd $(FRONTEND) && npm run dev
