set default-list := true

start:
    docker compose up --watch

build:
    docker compose build

test:
    docker compose run --rm api uv run pytest -vvv ./src/tests
