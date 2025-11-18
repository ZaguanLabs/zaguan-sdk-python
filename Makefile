.PHONY: help clean build check test publish publish-test install dev-install

help:
	@echo "Zaguan SDK - Available commands:"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make build         - Build the package"
	@echo "  make check         - Check package validity"
	@echo "  make test          - Run tests"
	@echo "  make publish-test  - Publish to Test PyPI"
	@echo "  make publish       - Publish to PyPI"
	@echo "  make install       - Install package locally"
	@echo "  make dev-install   - Install in development mode"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info zaguan_sdk.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	@echo "Building package..."
	python -m build

check: build
	@echo "Checking package..."
	python -m twine check dist/*

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

publish-test: check
	@echo "Publishing to Test PyPI..."
	python -m twine upload --repository testpypi dist/*
	@echo "Test installation with:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ zaguan-sdk"

publish: check test
	@echo "Publishing to PyPI..."
	python -m twine upload dist/*
	@echo "Package published! Install with:"
	@echo "  pip install zaguan-sdk"

install:
	@echo "Installing package..."
	pip install .

dev-install:
	@echo "Installing in development mode..."
	pip install -e .
	pip install -r requirements.txt

# Version management
version:
	@python -c "from zaguan_sdk import __version__; print(f'Current version: {__version__}')"

# Quick development workflow
dev: clean dev-install test
	@echo "Development environment ready!"
