from graphql import GraphQLScalarType


def anyvalue_parse_literal(node):
    # TODO: pass through parsed object if JSON?
    raise NotImplementedError()


AnyValue = GraphQLScalarType(
    name='AnyValue',
    description='JSON data with no fixed schema',
    serialize=lambda x: x,
    parse_literal=anyvalue_parse_literal,
    parse_value=lambda x: x)
