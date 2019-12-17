import logging

from flask import Flask, redirect
from flask_cors import CORS
from flask_sockets import Sockets

from .auth import load_auth_info
from .graphql_view import GraphQLView
from .subscriptions import SubscriptionServer

logger = logging.getLogger(__name__)


def create_graphql_app(schema):

    app = Flask(__name__)

    @app.route('/')
    def index():
        return redirect('/graphql')

    # GraphQL endpoints ----------------------------------------------

    app.add_url_rule(
        '/graphql',
        view_func=load_auth_info(GraphQLView.as_view(
            'graphql', schema=schema, graphiql=True)))

    # Optional, for adding batch query support (used in Apollo-Client)
    app.add_url_rule(
        '/graphql/batch',
        view_func=load_auth_info(GraphQLView.as_view(
            'graphql-batch', schema=schema, batch=True)))

    # Websockets -----------------------------------------------------

    sockets = Sockets(app)
    app.app_protocol = lambda environ_path_info: 'graphql-ws'
    subscription_server = SubscriptionServer(schema)

    @sockets.route('/subscriptions')
    def echo_socket(ws):
        subscription_server.handle(ws)
        return []

    # Add CORS support -----------------------------------------------

    CORS(app)

    return app
