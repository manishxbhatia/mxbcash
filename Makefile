.PHONY: dev build start test install-backend install-frontend

VENV = backend/.venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn
ALEMBIC = $(VENV)/bin/alembic
PYTEST = $(VENV)/bin/pytest

# ── Setup ──────────────────────────────────────────────────────────────────────

install-backend:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

# ── Database ───────────────────────────────────────────────────────────────────

migrate:
	cd backend && $(ALEMBIC) upgrade head

# ── Development ────────────────────────────────────────────────────────────────

dev-backend:
	$(UVICORN) app.main:app --reload --port 8000 --app-dir backend

dev-frontend:
	cd frontend && npm run dev

# Run backend and frontend concurrently
dev:
	@echo "Starting backend (port 8000) and frontend (port 5173)…"
	@trap 'kill %1 %2 2>/dev/null' EXIT; \
	$(UVICORN) app.main:app --reload --port 8000 --app-dir backend & \
	cd frontend && npm run dev & \
	wait

# ── Tests ──────────────────────────────────────────────────────────────────────

test:
	$(PYTEST) backend/tests/ -v

# ── Production build ───────────────────────────────────────────────────────────

build: install-frontend
	cd frontend && npm run build
	rm -rf backend/app/static
	mkdir -p backend/app/static
	cp -r frontend/dist/. backend/app/static/
	@echo "Frontend built and copied to backend/app/static/"

start:
	$(UVICORN) app.main:app --port 8000 --app-dir backend
