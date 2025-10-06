.PHONY: help dev test lint format db clean install

help:
	@echo "House Manuals - Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make dev       - Run development server"
	@echo "  make test      - Run tests with coverage"
	@echo "  make lint      - Run linter"
	@echo "  make format    - Format code with ruff"
	@echo "  make db        - Run database migrations"
	@echo "  make clean     - Clean cache and temporary files"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	flask run --debug --host=0.0.0.0 --port=5000

test:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

db:
	flask db upgrade

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/
