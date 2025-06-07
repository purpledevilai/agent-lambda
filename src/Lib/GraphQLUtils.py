from typing import Any
from graphql import (
    GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString,
    GraphQLFloat, GraphQLInt, GraphQLBoolean, GraphQLList, GraphQLArgument,
    graphql_sync, print_schema
)


def _build_type(value: Any, name: str = "Auto"):
    if isinstance(value, dict):
        return GraphQLObjectType(
            name,
            lambda: {
                k: GraphQLField(_build_type(v, f"{name}_{k.capitalize()}"))
                for k, v in value.items()
            },
        )
    elif isinstance(value, list):
        if value:
            return GraphQLList(_build_type(value[0], f"{name}Item"))
        else:
            return GraphQLList(GraphQLString)
    elif isinstance(value, bool):
        return GraphQLBoolean
    elif isinstance(value, int):
        return GraphQLInt
    elif isinstance(value, float) or type(value).__name__ == 'Decimal':
        return GraphQLFloat
    else:
        return GraphQLString


def create_schema(data: dict, update_resolver=None) -> GraphQLSchema:
    """Create a GraphQL schema representing ``data``.

    Parameters
    ----------
    data: dict
        The JSON object to represent.
    update_resolver: callable | None
        If provided, called with ``path`` and ``value`` when the ``update``
        mutation is executed. It should return the updated root object.
    """

    query_type = GraphQLObjectType(
        "Query",
        lambda: {
            k: GraphQLField(_build_type(v, k.capitalize())) for k, v in data.items()
        },
    )

    if update_resolver is None:
        def update_resolver(path=None, value=None):
            return data

    mutation_type = GraphQLObjectType(
        "Mutation",
        {
            "update": GraphQLField(
                query_type,
                args={
                    "path": GraphQLArgument(GraphQLString),
                    "value": GraphQLArgument(GraphQLString),
                },
                resolve=lambda obj, info, path=None, value=None: update_resolver(path, value),
            )
        },
    )

    return GraphQLSchema(query=query_type, mutation=mutation_type)


def get_value_at_path(data: Any, path: str) -> Any:
    if not path:
        return data
    current = data
    for part in path.split('.'):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            if idx < 0 or idx >= len(current):
                raise Exception("Index out of range", 400)
            current = current[idx]
        else:
            raise Exception("Invalid path", 400)
    return current


def set_value_at_path(data: Any, path: str, value: Any) -> Any:
    if not path:
        return value
    parts = path.split('.')
    current = data
    for part in parts[:-1]:
        if isinstance(current, dict):
            current = current.setdefault(part, {})
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            while idx >= len(current):
                current.append({})
            current = current[idx]
        else:
            raise Exception("Invalid path", 400)
    last = parts[-1]
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list) and last.isdigit():
        idx = int(last)
        while idx >= len(current):
            current.append(None)
        current[idx] = value
    else:
        raise Exception("Invalid path", 400)
    return data


def schema_to_sdl(schema: GraphQLSchema) -> str:
    return print_schema(schema)


def execute_query(schema: GraphQLSchema, query: str, root: dict):
    return graphql_sync(schema, query, root_value=root)
