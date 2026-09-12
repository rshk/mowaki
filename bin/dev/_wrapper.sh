#!/bin/bash

COMMAND="$( basename "$0" )"

case "$COMMAND" in
    start)
        # Ensure containers are up to date before starting.
        # This is pretty quick due to caching, but prevents headaches
        # caused by running outdated code when restarting containers.
        docker compose build

        # Start docker containers, enabling watch. Notice that "watch"
        # will only update code in the *running* containers, but
        # changes are lost on restart (requiring the "build" step
        # above).
        exec docker compose up --watch
        ;;

    stop)
        exec docker compose down
        ;;

    build)
        exec docker compose build
        ;;

    test)
        exec docker compose exec api uv run pytest -vvv ./src/tests
        ;;

    test-cov)
        exec docker compose exec api uv run pytest -vvv ./src/tests \
             --cov=app --cov-report=term-missing
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
