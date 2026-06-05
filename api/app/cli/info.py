import click
import json

from app.config import get_config_from_env

@click.group(name="info")
def grp_info():
    pass


@grp_info.command(name="config")
def cmd_info_config():
    cfg = get_config_from_env()
    print(json.dumps(cfg.model_dump(mode="json"), indent=4))
