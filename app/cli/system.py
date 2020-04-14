import logging

import click

from app.app import create_app
from app.db import db
from app.db.schema import metadata

from .base import cli

logger = logging.getLogger(__name__)


@cli.command(name="run")
@click.option("--host", "-h", default="127.0.0.1")
@click.option("--port", "-p", type=int, default=5000)
@click.option("--debugger/--no-debugger", is_flag=True, default=False)
@click.option(
    "use_reloader", "--reload/--no-reload", is_flag=True, default=True)
def cmd_run(host, port, debugger, use_reloader):
    """Run a development server.

    This is a replacement for the default "run" command from flask CLI.

    Will use WSGIServer and WebSocketHandler from gevent to properly
    handle websocket connections.

    Note that reloading uses an undocumented API from werkzeug, that
    might stop working in the future.

    Another option would be to use gunicorn, but keep in mind it only
    works on Unix-like systems::

        gunicorn -k flask_sockets.worker app.dev:app \
            --reload --bind localhost:5000
    """

    from werkzeug._reloader import run_with_reloader

    def _run_development_server():

        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler

        app = create_app()
        app.debug = debugger
        server = pywsgi.WSGIServer(
            (host, port), app, handler_class=WebSocketHandler, log=logger
        )
        server.serve_forever()

    if use_reloader:
        # WARNING: This is an undocumented API
        return run_with_reloader(_run_development_server)

    return _run_development_server()


@cli.group(name="db")
def grp_db():
    """Database administration tools. Mainly for development."""
    pass


@grp_db.command(name='create')
def cmd_db_create():
    """Create database schema"""
    engine = db.get_engine()
    metadata.create_all(engine)


@grp_db.command(name='drop')
@click.option('-y', '--yes', is_flag=True, default=False,
              prompt="Are you sure you want to delete the "
              "whole database, including data?")
def cmd_db_drop(yes):
    """Drop database schema"""
    if not yes:
        print('Skipping')
        return

    engine = db.get_engine()
    metadata.drop_all(engine)
