lint:
		uv run pre-commit run --all

run:
		uv run start-app

all:
		uv run pre-commit run --all
		uv run pytest
		uv run start-app

pyt:
		uv run pytest

pytv:
		uv run pytest -v


cov:
		uv run pytest --cov=src --cov-report=term-missing

coverage:
		uv run pytest --cov=src --cov-report=term-missing --cov-report=html
