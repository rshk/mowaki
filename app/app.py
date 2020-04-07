import logging

from app.api import schema
from app.lib.graphql_app import create_graphql_app

logger = logging.getLogger(__name__)


def create_app():
    app = create_graphql_app(schema.compile())
    return app


def setup_logging(debug=True):
    from nicelog import setup_logging

    # Use nicelog for prettier logging output.
    # Will also take care of adding a StreamHandler to standard error.
    setup_logging(debug=debug)

    # Log a DEBUG message to indicate whether debug logging is active.
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug('Debugging logger enabled')

    # Disable DEBUG logging for extra-verbose loggers
    logging.getLogger('Rx').setLevel(logging.INFO)
