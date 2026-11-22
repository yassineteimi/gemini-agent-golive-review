.PHONY: install test lint format run

install:
	uv sync --locked

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

# Interactive chat with the agent. Runs on the stub model unless AGENT_MODEL_MODE=gemini.
run:
	uv run adk run agent
