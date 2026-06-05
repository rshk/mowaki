import click
from . import info

cli = click.Group()
cli.add_command(info.grp_info)
