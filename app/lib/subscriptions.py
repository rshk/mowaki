import asyncio
import json
import logging
from collections import OrderedDict

from geventwebsocket.exceptions import WebSocketError
from graphql import format_error, graphql
# from graphql.execution.executors.sync import SyncExecutor
from rx import Observable
from rx.core.typing import Observer

from .auth import get_socket_context

GRAPHQL_WS = "graphql-ws"
WS_PROTOCOL = GRAPHQL_WS

GQL_CONNECTION_INIT = "connection_init"  # Client -> Server
GQL_CONNECTION_ACK = "connection_ack"  # Server -> Client
GQL_CONNECTION_ERROR = "connection_error"  # Server -> Client

# NOTE: This one here don't follow the standard due to connection optimization
GQL_CONNECTION_TERMINATE = "connection_terminate"  # Client -> Server
GQL_CONNECTION_KEEP_ALIVE = "ka"  # Server -> Client
GQL_START = "start"  # Client -> Server
GQL_DATA = "data"  # Server -> Client
GQL_ERROR = "error"  # Server -> Client
GQL_COMPLETE = "complete"  # Server -> Client
GQL_STOP = "stop"  # Client -> Server

# from .base import (
#     BaseConnectionContext, BaseSubscriptionServer, ConnectionClosedException)
# from .constants import GQL_CONNECTION_ACK, GQL_CONNECTION_ERROR

logger = logging.getLogger(__name__)


class ConnectionClosedException(Exception):
    pass


class BaseConnectionContext(object):
    def __init__(self, ws, request_context=None):
        self.ws = ws
        self.operations = {}
        self.request_context = request_context

    def has_operation(self, op_id):
        return op_id in self.operations

    def register_operation(self, op_id, async_iterator):
        self.operations[op_id] = async_iterator

    def get_operation(self, op_id):
        return self.operations[op_id]

    def remove_operation(self, op_id):
        del self.operations[op_id]

    def receive(self):
        raise NotImplementedError("receive method not implemented")

    def send(self, data):
        raise NotImplementedError("send method not implemented")

    @property
    def closed(self):
        raise NotImplementedError("closed property not implemented")

    def close(self, code):
        raise NotImplementedError("close method not implemented")


class GeventConnectionContext(BaseConnectionContext):
    def receive(self):
        msg = self.ws.receive()
        return msg

    def send(self, data):
        if self.closed:
            return
        self.ws.send(data)

    @property
    def closed(self):
        return self.ws.closed

    def close(self, code):
        self.ws.close(code)


class BaseSubscriptionServer(object):
    def __init__(self, schema, keep_alive=True):
        self.schema = schema
        self.keep_alive = keep_alive

    def get_graphql_params(self, connection_context, payload):
        return {
            "request_string": payload.get("query"),
            "variable_values": payload.get("variables"),
            "operation_name": payload.get("operationName"),
            "context_value": payload.get("context"),
        }

    def build_message(self, id, op_type, payload):
        message = {}
        if id is not None:
            message["id"] = id
        if op_type is not None:
            message["type"] = op_type
        if payload is not None:
            message["payload"] = payload
        return message

    def process_message(self, connection_context, parsed_message):
        op_id = parsed_message.get("id")
        op_type = parsed_message.get("type")
        payload = parsed_message.get("payload")

        if op_type == GQL_CONNECTION_INIT:
            return self.on_connection_init(connection_context, op_id, payload)

        elif op_type == GQL_CONNECTION_TERMINATE:
            return self.on_connection_terminate(connection_context, op_id)

        elif op_type == GQL_START:
            assert isinstance(payload, dict), "The payload must be a dict"

            params = self.get_graphql_params(connection_context, payload)
            if not isinstance(params, dict):
                error = Exception(
                    "Invalid params returned from get_graphql_params!"
                    " Return values must be a dict."
                )
                return self.send_error(connection_context, op_id, error)

            # If we already have a subscription with this id, unsubscribe from
            # it first
            if connection_context.has_operation(op_id):
                self.unsubscribe(connection_context, op_id)

            return self.on_start(connection_context, op_id, params)

        elif op_type == GQL_STOP:
            return self.on_stop(connection_context, op_id)

        else:
            return self.send_error(
                connection_context,
                op_id,
                Exception("Invalid message type: {}.".format(op_type)),
            )

    def send_execution_result(self, connection_context, op_id, execution_result):
        result = self.execution_result_to_dict(execution_result)
        return self.send_message(connection_context, op_id, GQL_DATA, result)

    def execution_result_to_dict(self, execution_result):
        result = OrderedDict()
        if execution_result.data:
            result["data"] = execution_result.data
        if execution_result.errors:
            result["errors"] = [
                format_error(error) for error in execution_result.errors
            ]
        return result

    def send_message(self, connection_context, op_id=None, op_type=None, payload=None):
        message = self.build_message(op_id, op_type, payload)
        assert message, "You need to send at least one thing"
        json_message = json.dumps(message)
        return connection_context.send(json_message)

    def send_error(self, connection_context, op_id, error, error_type=None):
        if error_type is None:
            error_type = GQL_ERROR

        assert error_type in [GQL_CONNECTION_ERROR, GQL_ERROR], (
            "error_type should be one of the allowed error messages"
            " GQL_CONNECTION_ERROR or GQL_ERROR"
        )

        error_payload = {"message": str(error)}

        return self.send_message(connection_context, op_id, error_type, error_payload)

    def unsubscribe(self, connection_context, op_id):
        if connection_context.has_operation(op_id):
            # Close async iterator
            connection_context.get_operation(op_id).dispose()
            # Close operation
            connection_context.remove_operation(op_id)
        self.on_operation_complete(connection_context, op_id)

    def on_operation_complete(self, connection_context, op_id):
        pass

    def on_connection_terminate(self, connection_context, op_id):
        return connection_context.close(1011)

    def execute(self, request_context, params):
        coro = graphql(self.schema, **dict(params, allow_subscriptions=True))
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    def handle(self, ws, request_context=None):
        raise NotImplementedError("handle method not implemented")

    def on_message(self, connection_context, message):
        try:
            if not isinstance(message, dict):
                parsed_message = json.loads(message)
                assert isinstance(parsed_message, dict), "Payload must be an object."
            else:
                parsed_message = message
        except Exception as e:
            return self.send_error(connection_context, None, e)

        return self.process_message(connection_context, parsed_message)

    def on_open(self, connection_context):
        raise NotImplementedError("on_open method not implemented")

    def on_connect(self, connection_context, payload):
        raise NotImplementedError("on_connect method not implemented")

    def on_close(self, connection_context):
        raise NotImplementedError("on_close method not implemented")

    def on_connection_init(self, connection_context, op_id, payload):
        raise NotImplementedError("on_connection_init method not implemented")

    def on_stop(self, connection_context, op_id):
        raise NotImplementedError("on_stop method not implemented")

    def on_start(self, connection_context, op_id, params):
        raise NotImplementedError("on_start method not implemented")


class GeventSubscriptionServer(BaseSubscriptionServer):
    def get_graphql_params(self, *args, **kwargs):
        params = super(GeventSubscriptionServer, self).get_graphql_params(
            *args, **kwargs
        )
        # return dict(params, executor=SyncExecutor())
        return dict(params)

    def handle(self, ws, request_context=None):
        connection_context = GeventConnectionContext(ws, request_context)
        self.on_open(connection_context)
        while True:
            try:
                if connection_context.closed:
                    raise ConnectionClosedException()
                message = connection_context.receive()
            except ConnectionClosedException:
                self.on_close(connection_context)
                return
            self.on_message(connection_context, message)

    def on_open(self, connection_context):
        pass

    def on_connect(self, connection_context, payload):
        pass

    def on_close(self, connection_context):
        remove_operations = list(connection_context.operations.keys())
        for op_id in remove_operations:
            self.unsubscribe(connection_context, op_id)

    def on_connection_init(self, connection_context, op_id, payload):
        try:
            self.on_connect(connection_context, payload)
            self.send_message(connection_context, op_type=GQL_CONNECTION_ACK)

        except Exception as e:
            self.send_error(connection_context, op_id, e, GQL_CONNECTION_ERROR)
            connection_context.close(1011)

    def on_start(self, connection_context, op_id, params):
        try:
            execution_result = self.execute(connection_context.request_context, params)
            assert isinstance(
                execution_result, Observable
            ), "A subscription must return an observable"
            execution_result.subscribe(
                SubscriptionObserver(
                    connection_context,
                    op_id,
                    self.send_execution_result,
                    self.send_error,
                    self.on_close,
                )
            )
        except Exception as e:
            self.send_error(connection_context, op_id, str(e))

    def on_stop(self, connection_context, op_id):
        self.unsubscribe(connection_context, op_id)


class SubscriptionObserver(Observer):
    def __init__(
        self, connection_context, op_id, send_execution_result, send_error, on_close
    ):
        self.connection_context = connection_context
        self.op_id = op_id
        self.send_execution_result = send_execution_result
        self.send_error = send_error
        self.on_close = on_close

    def on_next(self, value):
        self.send_execution_result(self.connection_context, self.op_id, value)

    def on_completed(self):
        self.on_close(self.connection_context)

    def on_error(self, error):
        self.send_error(self.connection_context, self.op_id, error)


class SubscriptionServer(GeventSubscriptionServer):
    def on_connect(self, connection_context, payload):
        logger.debug(
            "SubscriptionServer.on_connect(%s, %s)",
            repr(connection_context),
            repr(payload),
        )

        # TODO: is there a better way to pass context down, without
        # having to inject stuff into the connection context class??
        connection_context.auth_context = get_socket_context(payload)

    def on_message(self, connection_context, message):
        logger.debug("On Message: %s", repr((connection_context, message)))
        if message is None:
            self._dispose_subscription()
            return
        super().on_message(connection_context, message)

    def on_start(self, connection_context, op_id, params):

        try:
            execution_result = self.execute(connection_context.request_context, params)

            if not isinstance(execution_result, Observable):
                raise TypeError("A subscription must return a rx.Observable")

            observer = SubscriptionObserver(
                connection_context,
                op_id,
                self.send_execution_result,
                self.send_error,
                self.on_close,
            )

            self._subscription = execution_result.subscribe(observer)

        except WebSocketError as e:
            logger.debug("Web socket error (assuming closed): %s", repr(e))

        except BrokenPipeError:
            logger.debug("Socked closed")

        except Exception as e:
            logger.debug("Handling socket exception", exc_info=True)
            self.send_error(connection_context, op_id, str(e))

    def unsubscribe(self, *a, **kw):
        self._dispose_subscription()
        super().unsubscribe(*a, **kw)

    def _dispose_subscription(self):
        logger.debug("Disposing of subscription")
        if hasattr(self, "_subscription"):
            self._subscription.dispose()

    def get_graphql_params(self, connection_context, payload):
        _params = super().get_graphql_params(connection_context, payload)
        return {**_params, "context_value": connection_context.auth_context}
