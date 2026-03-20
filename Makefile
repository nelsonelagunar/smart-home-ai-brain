.PHONY: help install run test lint format clean docker-build docker-run

help: ## Show this help message
	@echo "Smart Home AI Brain - Makefile"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

run: ## Run the application
	source venv/bin/activate
	python -m smart_home_brain.main

test: ## Run tests
	source venv/bin/activate
	pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run linters
	source venv/bin/activate
	ruff check src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Format code
	source venv/bin/activate
	black src/ tests/
	isort src/ tests/

clean: ## Clean up
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

docker-build: ## Build Docker image
	docker build -t smart-home-ai-brain:latest .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

update-deps: ## Update dependencies
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
	pip install -r requirements-dev.txt --upgrade

check-ollama: ## Check if Ollama is running
	@curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama is running" || echo "✗ Ollama is not running"

pull-model: ## Pull Llama model
	ollama pull llama3.2

dev: ## Run in development mode with auto-reload
	source venv/bin/activate
	uvicorn smart_home_brain.main:app --reload --host 0.0.0.0 --port 8000