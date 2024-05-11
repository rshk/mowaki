import click
import uvicorn
from uvicorn.config import LOGGING_CONFIG

from app.config import create_config_from_env


def run_server(debug=False):
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
@click.option("--debug", is_flag=True, default=False)
def main(debug):
    run_server(debug=debug)


if __name__ == "__main__":
    main()
