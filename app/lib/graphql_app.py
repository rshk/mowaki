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

    @app.route("/")
    def index():
        return redirect("/graphql")

    # GraphQL endpoints ----------------------------------------------
    graphql_view = GraphQLView.as_view("graphql", schema=schema, graphiql=True)
    app.add_url_rule("/graphql", view_func=load_auth_info(graphql_view))

    # Optional, for adding batch query support (used in Apollo-Client)
    graphql_batch_view = GraphQLView.as_view("graphql-batch", schema=schema, batch=True)
    app.add_url_rule("/graphql/batch", view_func=load_auth_info(graphql_batch_view))

    # Websockets -----------------------------------------------------

    sockets = Sockets(app)

    # Used by geventwebsocket to upgrade connection, if the protocol
    # is valid. Requested protocol "graphql-ws" is passed by the
    # client in the upgrade request.
    app.app_protocol = lambda environ_path_info: "graphql-ws"

    @sockets.route("/subscriptions")
    def subscriptions_socket(ws):
        print(f"SUBSCRIPTION {ws}", flush=True)
        # subscription_server.handle(ws)
        return []

    # Add CORS support -----------------------------------------------

    CORS(app)

    return app
