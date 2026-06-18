import click

from . import db, info

cli = click.Group()
cli.add_command(info.grp_info)
cli.add_command(db.grp_db)
