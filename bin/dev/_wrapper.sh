#!/bin/bash

COMMAND="$( basename "$0" )"

if [ "$COMMAND" == "tool" ]; then
    COMMAND="$1"
    shift 1
fi

function print_commands_help() {
    echo "Available commands:"
    echo "TODO"
}

function style_fix_all() {
    style_fix_py
    style_fix_js
}

function style_fix_py() {
    uvx ruff@latest check --fix .
    uvx ruff@latest format .
}

function style_fix_js() {
    cd web && (
        npm run check -- --write
        npm run format -- --write
    )
}

function style_check_all() {
    style_check_py
    style_check_js
}

function style_check_py() {
    uvx ruff@latest check .
    uvx ruff@latest format --check .
}

function style_check_js() {
    cd web && (
        npm run check
        npm run format
    )
}


case "$COMMAND" in
    start)
        # Start docker containers

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
        # Stop docker containers
        exec docker compose down
        ;;

    build)
        # Build docker containers
        exec docker compose build
        ;;

    test)
        # Run the Python test suite
        exec docker compose exec api uv run pytest -vvv ./src/tests
        ;;

    test-cov)
        # Run the Python test suite, with coverage reporting
        exec docker compose exec api uv run pytest -vvv ./src/tests \
             --cov=app --cov-report=term-missing
        ;;

    style-fix)
        # Fix code to match linting and formatting rules
        style_fix_all ;;

    style-fix-py) style_fix_py ;;
    style-fix-js) style_fix_js ;;

    style-check)
        # Check linting and formatting rules, without writing
        style_check_all ;;

    style-check-py) style_check_py ;;
    style-check-js) style_check_js ;;

    psql)
        exec docker compose exec db psql
        ;;

    cli)
        # Run the Python app CLI
        exec docker compose exec api uv run app-cli "$@"
        ;;

    migrate)
        # Run database migrations
        exec docker compose exec api uv run alembic upgrade head
        ;;

    alembic)
        # Invoke Alembic to manage database migrations
        exec docker compose exec api uv run "$COMMAND" "$@"
        ;;

    install-py)
        exec uv sync --group dev
        ;;

    install-js)
        cd web && exec npm install
        ;;

    docs)
        exec uv run make -C docs help
        ;;

    docs-watch)
        exec uv run sphinx-autobuild docs docs/_build/html -b html
        ;;

    "") print_commands_help ;;

    _wrapper.sh)
        echo "Do not call this command directly, use a qualified symlink instead"
        exit 3
        ;;

    *)
        echo "Unknown command: ${COMMAND}"
        exit 2
        ;;
esac
