import click
import uvicorn

from app.config import config_context, create_config_from_env
from app.resources import initialize_resources, resources_context


def run_server(debug=False):
    """
    Args:
        debug: Enable development mode
    """

    cfg = create_config_from_env()
    with config_context(cfg):
        resources = initialize_resources(cfg)
        with resources_context(resources):
            options = {
                "host": cfg.bind_host,
                "port": cfg.port,
                "log_level": "debug" if debug else "info",
            }

            if debug:
                options["reload"] = True
            else:
                # TODO: allow configuring number of workers
                options["workers"] = 1

            uvicorn.run("app.webapi.webapp:create_app", factory=True, **options)


@click.command()
@click.option("--debug", is_flag=True, default=False)
def main(debug):
    run_server(debug=debug)


if __name__ == "__main__":
    main()
