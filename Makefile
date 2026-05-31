.PHONY: help install run lint format mypy check-all pre-commit

help: ## Show available targets
	@echo "🔍 Displaying help:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using poetry
	@echo "📦 Installing dependencies..."
	@poetry install

run: ## Run the application
	@echo "🚀 Running application..."
	@poetry run python -m app

lint: ## Lint the code with Ruff
	@echo "🔍 Linting code..."
	@poetry run ruff check app

format: ## Format the code with Ruff
	@echo "🖋️ Formatting code..."
	@poetry run ruff format app

mypy: ## Check types with MyPy
	@echo "🔍 Checking types with MyPy..."
	@poetry run mypy app

check-all: format lint mypy ## Run all linters

migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."; poetry run alembic upgrade head

pre-commit: ## Install pre-commit hooks
	@echo "🔗 Installing pre-commit hooks..."
	@pre-commit install

%:
	@:
