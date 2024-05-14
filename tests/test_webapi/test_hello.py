import pytest
from starlette.testclient import TestClient

from app.webapi.webapp import create_app

# from app.webapi.schema import schema


@pytest.fixture
def testclient(config):
    app = create_app(config)
    return TestClient(app)


@pytest.mark.asyncio
async def test_execute_graphql_query(testclient):
    response = testclient.post("/graphql", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello world"}}


@pytest.mark.asyncio
async def test_execute_graphql_query_with_hardcoded_argument(testclient):
    response = testclient.post("/graphql", json={"query": '{ hello(name:"Alice") }'})
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello Alice"}}


@pytest.mark.asyncio
async def test_execute_graphql_query_with_variables(testclient):
    query = """
    query($name: String){
        hello(name: $name)
    }
    """
    variables = {"name": "Bob"}
    response = testclient.post(
        "/graphql", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello Bob"}}
