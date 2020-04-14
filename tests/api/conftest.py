import pytest

from app.app import create_app


class GraphQLTestClient:

    def __init__(self, flask_test_client):
        self._client = flask_test_client

    def execute(
            self,
            query,
            variables=None,
            operation_name=None,
            token=None):

        body = {'query': query}

        if variables is not None:
            body['variables'] = variables

        if operation_name is not None:
            body['operationName'] = variables

        headers = {}

        if token is not None:
            headers['Authorization'] = 'Bearer {}'.format(token)

        response = self._client.post(
            path='/graphql',
            headers=headers,
            json=body)

        # TODO: handle non-200 codes
        return response


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield GraphQLTestClient(client)
