import click
from flask.cli import FlaskGroup

from app.app import create_app, setup_logging


@click.group(cls=FlaskGroup, create_app=create_app)
@click.option('--debug', is_flag=True, default=False)
def cli(debug):
    setup_logging(debug=debug)
