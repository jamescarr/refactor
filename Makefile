.PHONY: install clean dev lint test test-cov

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev,test]"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv pip install ruff
	ruff check .

test:
	pytest

test-cov:
	pytest --cov=refactor --cov-report=html

.DEFAULT_GOAL := install 