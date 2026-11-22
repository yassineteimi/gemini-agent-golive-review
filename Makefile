.PHONY: install test smoke lint format run

install:
	uv sync --locked

test:
	uv run pytest

# The stub agent against the real data/ documents (tests/smoke/questions.json).
smoke:
	uv run pytest -m smoke

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

# Interactive chat with the agent. Runs on the stub model unless AGENT_MODEL_MODE=gemini.
run:
	uv run adk run agent
