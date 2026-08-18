#!/bin/bash

COMMAND="$( basename "$0" )"

case "$COMMAND" in
    start)
        exec docker compose up --watch
        ;;

    stop)
        exec docker compose down
        ;;

    build)
        exec docker compose build
        ;;

    test)
        exec docker compose run --rm api uv run pytest -vvv ./src/tests
        ;;

    style-fix)
        # Fix code to match linting and formatting rules
        uvx ruff@latest check --fix .
        uvx ruff@latest format .
        ;;

    style-check)
        # Check linting and formatting rules
        uvx ruff@latest check .
        uvx ruff@latest format --check .
        ;;

    psql)
        exec docker compose exec db psql
        ;;

    cli)
        exec docker compose exec api uv run app-cli "$@"
        ;;

    migrate)
        exec docker compose exec api uv run alembic upgrade head
        ;;

    alembic)
        exec docker compose exec api uv run "$COMMAND" "$@"
        ;;

    install)
        exec uv sync --group dev
        ;;

    docs)
        exec uv run make -C docs help
        ;;

    docs-watch)
        exec uv run sphinx-autobuild docs docs/_build/html -b html
        ;;

    _wrapper.sh)
        echo "Do not call this command directly, use a qualified symlink instead"
        exit 3
        ;;

    *)
        echo "Unknown command: ${COMMAND}"
        exit 2
        ;;
esac
