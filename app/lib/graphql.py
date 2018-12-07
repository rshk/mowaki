from graphql.type.definition import GraphQLScalarType


GraphQLFileUpload = GraphQLScalarType(
    name="FileUpload",
    description="Field for file uploads",
    serialize=lambda value: None,
    parse_value=lambda node: node,
    parse_literal=lambda value: value,
)
