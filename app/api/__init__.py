import logging
import time
from datetime import datetime
from typing import List

from pyql import Object, Schema
from rx import Observable

from app.db.query.example import (
    create_note, delete_note, get_note, list_notes, update_note)
from app.lib.graphql import GraphQLFileUpload

logger = logging.getLogger(__name__)

# from rx import Observable

schema = Schema()


Note = Object('Note', {
    'id': int,
    'title': str,
    'body': str,
})


@schema.query.field('list_notes')
def resolve_list_notes(root, info) -> List[Note]:
    notes = [_node_from_record(x) for x in list_notes()]
    logger.debug('NOTES: %s', repr(notes))
    return notes


@schema.query.field('get_note')
def resolve_get_note(root, info, id: int) -> Note:
    note = _node_from_record(get_note(id))
    logger.debug('NOTE (%s): %s', id, repr(note))
    return note


def _node_from_record(record):
    return Note(
        id=record.id,
        title=record.title,
        body=record.body)


CreateNoteResult = Object('CreateNoteResult', {'ok': bool, 'note_id': int})
UpdateNoteResult = Object('UpdateNoteResult', {'ok': bool})
DeleteNoteResult = Object('DeleteNoteResult', {'ok': bool})
UploadNoteResult = Object('UploadNoteResult', {
    'ok': bool,
    'note_id': int,
    'title': str,
    'body': str,
})


@schema.mutation.field('create_note')
def resolve_create_note(
        root, info, title: str, body: str = None) -> CreateNoteResult:

    note_id = create_note(title, body)
    return CreateNoteResult(ok=True, note_id=note_id)


@schema.mutation.field('update_note')
def resolve_update_note(
        root, info, id: int,
        title: str = None, body: str = None) -> UpdateNoteResult:

    update_note(id, title=title, body=body)
    return UpdateNoteResult(ok=True)


@schema.mutation.field('delete_note')
def resolve_delete_note(root, info, id: int) -> DeleteNoteResult:
    delete_note(id)
    return DeleteNoteResult(ok=True)


@schema.mutation.field('upload_note')
def resolve_upload_note(
        root, info, uploaded_file: GraphQLFileUpload) -> UploadNoteResult:

    title = uploaded_file.filename
    body = uploaded_file.stream.read().decode('utf-8')
    # TODO: ensure the file contains text, not binary data
    note_id = create_note(title=title, body=body)
    return UploadNoteResult(
        ok=True,
        note_id=note_id,
        title=title,
        body=body)


@schema.subscription.field('current_time')
def subscribe_current_time(root, info) -> str:
    return Observable.from_iterable(poll_current_time())


def poll_current_time():
    while True:
        yield datetime.utcnow().strftime('%H:%M:%S')
        time.sleep(1)
