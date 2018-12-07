import logging
from collections import namedtuple

from graphql.type import (
    GraphQLArgument, GraphQLBoolean, GraphQLField, GraphQLInt, GraphQLList,
    GraphQLNonNull, GraphQLObjectType, GraphQLSchema, GraphQLString)

from app.db.query.example import (
    create_note, delete_note, get_note, list_notes, update_note)
from app.lib.graphql import GraphQLFileUpload

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


def resolve_update_note(root, info, id, title=None, body=None):
    update_note(id, title=title, body=body)
    return UpdateNoteResult(ok=True)


def resolve_delete_note(root, info, id):
    delete_note(id)
    return DeleteNoteResult(ok=True)


def resolve_upload_note(root, info, uploadedFile):
    title = uploadedFile.filename
    body = uploadedFile.stream.read().decode('utf-8')
    # TODO: ensure the file contains text, not binary data
    note_id = create_note(title=title, body=body)
    return UploadNoteResult(
        ok=True,
        noteId=note_id,
        title=title,
        body=body,
    )


CreateNoteResult = namedtuple('CreateNoteResult', 'ok,noteId')
UpdateNoteResult = namedtuple('UpdateNoteResult', 'ok')
DeleteNoteResult = namedtuple('DeleteNoteResult', 'ok')
UploadNoteResult = namedtuple('UploadNoteResult', 'ok,noteId,title,body')


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

        'updateNote': GraphQLField(
            GraphQLObjectType(
                'UpdateNoteResult',
                fields=lambda: {
                    'ok': GraphQLField(GraphQLBoolean),
                },
            ),
            args={
                'id': GraphQLArgument(GraphQLInt),
                'title': GraphQLArgument(GraphQLString),
                'body': GraphQLArgument(GraphQLString),
            },
            resolver=resolve_update_note,
        ),

        'deleteNote': GraphQLField(
            GraphQLObjectType(
                'DeleteNoteResult',
                fields=lambda: {
                    'ok': GraphQLField(GraphQLBoolean),
                },
            ),
            args={
                'id': GraphQLArgument(GraphQLInt),
            },
            resolver=resolve_delete_note,
        ),

        'uploadNote': GraphQLField(
            GraphQLObjectType(
                'UploadNoteResult',
                fields=lambda: {
                    'ok': GraphQLField(GraphQLBoolean),
                    'noteId': GraphQLField(GraphQLInt),
                    'title': GraphQLField(GraphQLString),
                    'body': GraphQLField(GraphQLString),
                },
            ),
            args={
                'uploadedFile': GraphQLArgument(
                    (GraphQLFileUpload)),
            },
            resolver=resolve_upload_note,
        ),

    },
)


schema = GraphQLSchema(
    query=queryType,
    mutation=mutationType,
)
