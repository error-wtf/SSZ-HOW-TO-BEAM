.PHONY: help install test test-verbose test-cov simulations clean lint docs

help:
	@echo "BEAM-SSZ v0.6 - Available commands:"
	@echo ""
	@echo "  make install      - Install dependencies and package"
	@echo "  make test         - Run all tests (quick)"
	@echo "  make test-verbose - Run all tests (verbose)"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make simulations  - Run all simulation scripts"
	@echo "  make lint         - Run linting checks"
	@echo "  make docs         - Generate documentation"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make analyze      - Run bridge analysis"

install:
	bash scripts/install.sh

test:
	python -m pytest tests/ --tb=no -q

test-verbose:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=src/beam_ssz --cov-report=html
	simulations:
	@for f in simulations/*.py; do \
		echo "Running $$f..."; \
		python "$$f" 2>&1 | head -20; \
		echo ""; \
	done

analyze:
	python scripts/analyze_bridge.py --xi-a 0.1 --xi-b 0.2 --lambda 0.5

lint:
	@echo "Running linting..."
	python -m py_compile src/beam_ssz/*.py
	python -m py_compile src/beam_ssz/tensor/*.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

docs:
	@echo "Documentation is in docs/ directory"
	@ls -1 docs/

zip:
	cd .. && zip -r BEAM-SSZ_full_mathlab_v0.6.zip BEAM-SSZ-v0.6 \
		-x "BEAM-SSZ-v0.6/.venv/*" \
		-x "BEAM-SSZ-v0.6/**/__pycache__/*" \
		-x "BEAM-SSZ-v0.6/.pytest_cache/*"
