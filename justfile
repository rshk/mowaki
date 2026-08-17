set default-list := true

start:
    docker compose up --watch

build:
    docker compose build

test:
    docker compose run --rm api uv run pytest -vvv ./src/tests

style-fix:
    # Fix code to match linting and formatting rules
    uvx ruff@latest check --fix .
    uvx ruff@latest format .

style-check:
    # Check linting and formatting rules
    uvx ruff@latest check .
    uvx ruff@latest format --check .
