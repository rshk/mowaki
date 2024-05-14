import pytest

from app.webapi.schema import schema


@pytest.mark.asyncio
async def test_execute_graphql_query():
    result = await schema.execute(
        """
    {
        hello
    }
    """
    )

    assert result.errors is None
    assert result.data == {"hello": "Hello world"}


@pytest.mark.asyncio
async def test_execute_graphql_query_with_hardcoded_argument():
    result = await schema.execute(
        """
    {
        hello(name: "Alice")
    }
    """
    )

    assert result.errors is None
    assert result.data == {"hello": "Hello Alice"}


@pytest.mark.asyncio
async def test_execute_graphql_query_with_variables():
    result = await schema.execute(
        """
    query($name: String){
        hello(name: $name)
    }
    """,
        variable_values={"name": "Bob"},
    )

    assert result.errors is None
    assert result.data == {"hello": "Hello Bob"}
