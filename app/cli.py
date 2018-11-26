import logging

import click
from flask.cli import FlaskGroup

from .app import create_app, setup_logging

logger = logging.getLogger(__name__)


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass


@cli.command(name='run')
@click.option('--host', '-h', default='127.0.0.1')
@click.option('--port', '-p', type=int, default=5000)
@click.option('--debugger', '-d', is_flag=True, default=False)
def cmd_run(host, port, debugger):
    """Replace default "run" command from flask CLI.

    Will use WebSocketHandler to properly handle websocket
    connections.

    Note that this does not support reloading as werkzeug's
    development server does; to get that you need to run gunicorn,
    like this:

    gunicorn -k flask_sockets.worker app.dev:app --reload --bind localhost:5000
    """

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    setup_logging()

    app = create_app()
    app.debug = debugger
    server = pywsgi.WSGIServer(
        (host, port), app, handler_class=WebSocketHandler, log=logger)
    server.serve_forever()
