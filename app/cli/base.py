import logging

import click
from flask.cli import FlaskGroup

from app.app import create_app, setup_logging

logger = logging.getLogger(__name__)


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass


@cli.command(name='run')
@click.option('--host', '-h', default='127.0.0.1')
@click.option('--port', '-p', type=int, default=5000)
@click.option('--debugger/--no-debugger', is_flag=True, default=False)
@click.option('use_reloader', '--reload/--no-reload',
              is_flag=True, default=True)
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

        setup_logging()

        app = create_app()
        app.debug = debugger
        server = pywsgi.WSGIServer(
            (host, port), app, handler_class=WebSocketHandler, log=logger)
        server.serve_forever()

    if use_reloader:
        # WARNING: This is an undocumented API
        return run_with_reloader(_run_development_server)

    return _run_development_server()
