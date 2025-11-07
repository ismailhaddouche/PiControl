.PHONY: help install install-dev install-hardware install-all
.PHONY: test test-cov lint format type-check security-check
.PHONY: run run-dev clean clean-all
.PHONY: db-init db-backup db-restore

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
BLACK := $(VENV_BIN)/black
RUFF := $(VENV_BIN)/ruff
MYPY := $(VENV_BIN)/mypy
UVICORN := $(VENV_BIN)/uvicorn
SAFETY := $(VENV_BIN)/safety
BANDIT := $(VENV_BIN)/bandit

# Database configuration
DB_DIR := $(or $(PICONTROL_DB_DIR),/var/lib/picontrol)
DB_FILE := $(DB_DIR)/pi_control.db
BACKUP_DIR := $(or $(PICONTROL_BACKUP_DIR),/var/backups/picontrol)

help:  ## Show this help message
	@echo "PiControl - Makefile Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

## Installation targets

install: $(VENV)  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: $(VENV)  ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

install-hardware: $(VENV)  ## Install hardware dependencies (Raspberry Pi)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[hardware]"

install-all: $(VENV)  ## Install all dependencies (dev + hardware + security)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[all]"

$(VENV):  ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

## Development targets

run: $(VENV)  ## Run the application (production mode)
	@echo "Starting PiControl in production mode..."
	@echo "Access at: http://localhost:8000"
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

run-dev: $(VENV)  ## Run the application (development mode with reload)
	@echo "Starting PiControl in development mode..."
	@echo "Access at: http://localhost:8000"
	@echo "Auto-reload enabled"
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

## Testing targets

test: $(VENV)  ## Run tests
	PICONTROL_DB_DIR=.test_db $(PYTEST) tests/

test-cov: $(VENV)  ## Run tests with coverage report
	PICONTROL_DB_DIR=.test_db $(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term

test-watch: $(VENV)  ## Run tests in watch mode
	PICONTROL_DB_DIR=.test_db $(PYTEST) tests/ -f

## Code quality targets

lint: $(VENV)  ## Run linter (ruff)
	$(RUFF) check app/ tests/ tools/ scripts/

lint-fix: $(VENV)  ## Run linter and auto-fix issues
	$(RUFF) check --fix app/ tests/ tools/ scripts/

format: $(VENV)  ## Format code with black
	$(BLACK) app/ tests/ tools/ scripts/

format-check: $(VENV)  ## Check code formatting without changes
	$(BLACK) --check app/ tests/ tools/ scripts/

type-check: $(VENV)  ## Run type checker (mypy)
	$(MYPY) app/

security-check: $(VENV)  ## Run security checks (safety + bandit)
	@echo "Checking dependencies for vulnerabilities..."
	-$(SAFETY) check --json
	@echo "\nScanning code for security issues..."
	$(BANDIT) -r app/ -f json -o bandit-report.json || true
	@echo "Security scan complete. Check bandit-report.json for details."

check-all: lint format-check type-check  ## Run all code quality checks

## Database targets

db-init:  ## Initialize database (create tables)
	@echo "Initializing database..."
	@mkdir -p $(DB_DIR)
	PICONTROL_DB_DIR=$(DB_DIR) $(PYTHON) scripts/init_db.py
	@echo "Database initialized at $(DB_FILE)"

db-backup:  ## Backup database
	@echo "Backing up database..."
	@mkdir -p $(BACKUP_DIR)
	@if [ -f "$(DB_FILE)" ]; then \
		cp $(DB_FILE) $(BACKUP_DIR)/pi_control_$$(date +%Y%m%d_%H%M%S).db; \
		echo "Backup created in $(BACKUP_DIR)"; \
	else \
		echo "Error: Database file not found at $(DB_FILE)"; \
		exit 1; \
	fi

db-restore:  ## Restore database from backup (requires BACKUP_FILE=path)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: Please specify BACKUP_FILE=path"; \
		echo "Example: make db-restore BACKUP_FILE=/var/backups/picontrol/pi_control_20231106.db"; \
		exit 1; \
	fi
	@if [ ! -f "$(BACKUP_FILE)" ]; then \
		echo "Error: Backup file not found: $(BACKUP_FILE)"; \
		exit 1; \
	fi
	@echo "Restoring database from $(BACKUP_FILE)..."
	@mkdir -p $(DB_DIR)
	cp $(BACKUP_FILE) $(DB_FILE)
	@echo "Database restored successfully"

## Cleanup targets

clean:  ## Clean temporary files and caches
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml bandit-report.json
	rm -rf .test_db/
	@echo "Cleanup complete"

clean-all: clean  ## Clean everything including venv
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Full cleanup complete"

## Utility targets

freeze:  ## Freeze current dependencies to requirements-lock.txt
	$(PIP) freeze > requirements-lock.txt
	@echo "Dependencies frozen to requirements-lock.txt"

upgrade-deps:  ## Upgrade all dependencies
	$(PIP) install --upgrade -r requirements.txt
	@echo "Dependencies upgraded. Run 'make freeze' to lock versions."

pre-commit-install: $(VENV)  ## Install pre-commit hooks
	$(PIP) install pre-commit
	$(VENV_BIN)/pre-commit install
	@echo "Pre-commit hooks installed"

show-config:  ## Show current configuration
	@echo "Configuration:"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Virtual env: $(VENV)"
	@echo "  Database dir: $(DB_DIR)"
	@echo "  Database file: $(DB_FILE)"
	@echo "  Backup dir: $(BACKUP_DIR)"

logs:  ## Show recent application logs
	@echo "Recent application logs:"
	@if [ -f "uvicorn.log" ]; then tail -50 uvicorn.log; fi
	@if [ -f "admin_actions.log" ]; then echo "\nAdmin actions:"; tail -20 admin_actions.log; fi
