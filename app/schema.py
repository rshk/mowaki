import logging
from collections import namedtuple

from graphql.type import (
    GraphQLArgument, GraphQLBoolean, GraphQLEnumType, GraphQLEnumValue,
    GraphQLField, GraphQLInt, GraphQLInterfaceType, GraphQLList,
    GraphQLNonNull, GraphQLObjectType, GraphQLSchema, GraphQLString)

from app.db.query.example import (
    create_note, delete_note, get_note, list_notes, update_note)

logger = logging.getLogger(__name__)

NoteType = GraphQLObjectType(
    'Note',
    description='A note in the example app.',
    fields=lambda: {
        'id': GraphQLField(
            GraphQLNonNull(GraphQLInt),
            description='Note identifier',
        ),
        'title': GraphQLField(
            GraphQLNonNull(GraphQLString),
            description='Note title',
        ),
        'body': GraphQLField(
            GraphQLString,
            description='Note body',
        ),
    }
)


def resolve_list_notes(root, info):
    notes = list_notes()
    logger.debug('NOTES: %s', repr(notes))
    return notes


queryType = GraphQLObjectType(
    "Query",
    fields=lambda: {

        'listNotes': GraphQLField(
            GraphQLList(NoteType),
            args={},
            resolver=resolve_list_notes,
        ),

        'getNote': GraphQLField(
            NoteType,
            args={
                'id': GraphQLArgument(
                    description='id of the note',
                    type=GraphQLNonNull(GraphQLInt),
                ),
            },
            resolver=lambda root, info, id: get_note(id),
        ),

    },
)


def resolve_create_note(root, info, title, body=None):
    note_id = create_note(title, body)
    return CreateNoteResult(ok=True, noteId=note_id)


CreateNoteResult = namedtuple('CreateNoteResult', 'ok,noteId')


mutationType = GraphQLObjectType(
    'Mutation',
    fields=lambda: {
        'createNote': GraphQLField(
            GraphQLObjectType(
                'CreateNoteResult',
                fields=lambda: {
                    'ok': GraphQLField(GraphQLBoolean),
                    'noteId': GraphQLField(GraphQLInt),
                },
            ),
            args={
                'title': GraphQLArgument(
                    GraphQLNonNull(GraphQLString),
                ),
                'body': GraphQLArgument(
                    GraphQLString,
                    default_value=None,
                ),
            },
            resolver=resolve_create_note,
        ),
    },
)


schema = GraphQLSchema(
    query=queryType,
    mutation=mutationType,
)
