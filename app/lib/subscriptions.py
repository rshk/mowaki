import logging

from geventwebsocket.exceptions import WebSocketError
from graphql_ws.gevent import GeventSubscriptionServer, SubscriptionObserver
from rx import Observable

from .auth import get_socket_context

logger = logging.getLogger(__name__)


class SubscriptionServer(GeventSubscriptionServer):

    def on_connect(self, connection_context, payload):
        logger.debug('SubscriptionServer.on_connect(%s, %s)',
                     repr(connection_context), repr(payload))

        # TODO: is there a better way to pass context down, without
        # having to inject stuff into the connection context class??
        connection_context.auth_context = get_socket_context(payload)

    def on_message(self, connection_context, message):
        logger.debug('On Message: %s', repr((connection_context, message)))
        if message is None:
            self._dispose_subscription()
            return
        super().on_message(connection_context, message)

    def on_start(self, connection_context, op_id, params):

        try:
            execution_result = self.execute(
                connection_context.request_context, params)

            if not isinstance(execution_result, Observable):
                raise TypeError('A subscription must return a rx.Observable')

            observer = SubscriptionObserver(
                    connection_context,
                    op_id,
                    self.send_execution_result,
                    self.send_error,
                    self.on_close)

            self._subscription = execution_result.subscribe(observer)

        except WebSocketError as e:
            logger.debug('Web socket error (assuming closed): %s', repr(e))

        except BrokenPipeError:
            logger.debug('Socked closed')

        except Exception as e:
            logger.debug('Handling socket exception', exc_info=True)
            self.send_error(connection_context, op_id, str(e))

    def unsubscribe(self, *a, **kw):
        self._dispose_subscription()
        super().unsubscribe(*a, **kw)

    def _dispose_subscription(self):
        logger.debug('Disposing of subscription')
        if hasattr(self, '_subscription'):
            self._subscription.dispose()

    def get_graphql_params(self, connection_context, payload):
        _params = super().get_graphql_params(connection_context, payload)
        return {
            **_params,
            'context_value': connection_context.auth_context,
        }
