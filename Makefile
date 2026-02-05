lint:
		uv run pre-commit run --all

run:
		uv run start-app

all:
		uv run pre-commit run --all
		uv run start-app
