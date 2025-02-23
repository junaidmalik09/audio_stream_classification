.PHONY: format lint clean install dev-install help build run stop

# Default Python version
PYTHON := .venv/bin/python

# Formatting settings
LINE_LENGTH := 166

help:
	@echo "Available targets:"
	@echo "  format      - Format code using black and isort"
	@echo "  lint        - Run linting checks"
	@echo "  clean       - Remove Python cache files"
	@echo "  install     - Install production dependencies"
	@echo "  dev-install - Install development dependencies"
	@echo "  build       - Build Docker Compose images"
	@echo "  run         - Run Docker Compose services"
	@echo "  stop        - Stop Docker Compose services"

install:
	$(PYTHON) -m pip install -r requirements.txt

dev-install:
	$(PYTHON) -m pip install -r requirements-dev.txt

format:
	$(PYTHON) -m black backend --line-length $(LINE_LENGTH) --exclude extras --exclude .venv
	$(PYTHON) -m isort backend --profile black --line-length $(LINE_LENGTH) --skip extras --skip .venv

lint:
	$(PYTHON) -m black backend --line-length $(LINE_LENGTH) --exclude extras --exclude .venv
	$(PYTHON) -m isort backend --profile black --line-length $(LINE_LENGTH) --skip extras --skip .venv
	$(PYTHON) -m flake8 backend --max-line-length $(LINE_LENGTH) --exclude extras --exclude .venv

clean:
	find backend frontend -type d -name "__pycache__" -exec rm -rf {} +
	find backend frontend -type f -name "*.pyc" -delete
	find backend frontend -type f -name "*.pyo" -delete
	find backend frontend -type f -name "*.pyd" -delete 

build:
	docker compose build

run:
	docker compose up -d

stop:
	docker compose down -v
