import click
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import os


def run_server(*, host="127.0.0.1", port=8000, debug=False, reload=False, workers=1):
    """
    Args:
        debug: Enable development mode
    """

    # This configuration instance is only used to initialize uvicorn
    cfg = create_config_from_env()

    options = {
        "host": cfg.bind_host,
        "port": cfg.port,
        "log_level": "debug" if debug else "info",
        "log_config": get_logging_config(debug),
    }

    if debug:
        options["reload"] = True
    else:
        # TODO: allow configuring number of workers
        options["workers"] = 1  # Mutually exclusive with "reload"

    uvicorn.run("app.webapi.webapp:create_initialized_app", factory=True, **options)


def get_logging_config(debug):
    return {
        **LOGGING_CONFIG,
        "loggers": {
            **LOGGING_CONFIG["loggers"],
            "app": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["default"],
            },
        },
    }


@click.command()
@click.option("--host", envvar="BIND_HOST", default="127.0.0.1")
@click.option("--port", envvar="PORT", type=int, default=8000)
@click.option("--debug", is_flag=True, default=False)
@click.option("--reload", is_flag=True, default=False)
@click.option("--workers", type=int, envvar="WEB_CONCURRENCY", default=1)
def main(**kwargs):
    run_server(**kwargs)


if __name__ == "__main__":
    main()
