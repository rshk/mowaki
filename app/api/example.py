import logging
import time
from datetime import datetime
from typing import List

from pyql import InputObject, Object
from rx import Observable

from app.core.example import NotesCore
from app.core.exceptions import UserError
from app.lib.graphql import GraphQLFileUpload

from .base import schema

logger = logging.getLogger(__name__)


Note = Object('Note', {
    'id': int,
    'title': str,
    'text': str,
})


@Note.field('summary')
def resolve_note_summary(note, info, length: int = 100) -> str:

    if length < 0:
        raise ValueError('Invalid length: {}'.format(length))

    return (note.text or '')[:length]


# Note: list ---------------------------------------------------------

@schema.query.field('list_notes')
def resolve_list_notes(root, info) -> List[Note]:
    core = NotesCore.from_request()
    return list(core.list())


# Note: get ----------------------------------------------------------

@schema.query.field('get_note')
def resolve_get_note(root, info, id: int) -> Note:
    core = NotesCore.from_request()
    return core.get(id)


# Note: create -------------------------------------------------------

CreateNoteInput = InputObject('CreateNoteInput', {
    'title': str,
    'text': str,
})

CreateNoteOutput = Object('CreateNoteOutput', {
    'ok': bool,
    'note_id': int,
    'error_message': str,
})


@CreateNoteOutput.field('note')
def resolve_create_note_output_note(root, info) -> Note:
    core = NotesCore.from_request()
    return core.get(root.note_id)


@schema.mutation.field('create_note')
def resolve_create_note(
        root, info, data: CreateNoteInput = None) -> CreateNoteOutput:

    core = NotesCore.from_request()
    try:
        note_id = core.create(title=data.title, text=data.text)
    except UserError as e:
        return CreateNoteOutput(ok=False, error_message=str(e))

    return CreateNoteOutput(ok=True, note_id=note_id)


# Note: update -------------------------------------------------------

UpdateNoteInput = InputObject('UpdateNoteInput', {
    'title': str,
    'text': str,
})

UpdateNoteOutput = Object('UpdateNoteOutput', {
    'ok': bool,
    'note_id': int,
    'error_message': str,
})


@UpdateNoteOutput.field('note')
def resolve_update_note_output_note(root, info) -> Note:
    core = NotesCore.from_request()
    return core.get(root.note_id)


@schema.mutation.field('update_note')
def resolve_update_note(
        root,
        info,
        id: int,
        data: UpdateNoteInput) -> UpdateNoteOutput:

    core = NotesCore.from_request()
    note = core.get(id)
    core.update(note, title=data.title, text=data.text)
    return UpdateNoteOutput(ok=True, note_id=id)


# Note: delete -------------------------------------------------------

DeleteNoteOutput = Object('DeleteNoteOutput', {
    'ok': bool,
    'error_message': str,
})


@schema.mutation.field('delete_note')
def resolve_delete_note(root, info, id: int) -> DeleteNoteOutput:
    core = NotesCore.from_request()
    note = core.get(id)
    core.delete(note)
    return DeleteNoteOutput(ok=True)


# Note: upload -------------------------------------------------------

UploadNoteOutput = Object('UploadNoteOutput', {
    'ok': bool,
    'note_id': int,
    'note': Note,
    'error_message': str,
})


@UploadNoteOutput.field('note')
def resolve_upload_note_output_note(root, info) -> Note:
    core = NotesCore.from_request()
    return core.get(root.note_id)


@schema.mutation.field('upload_note')
def resolve_upload_note(
        root, info, uploaded_file: GraphQLFileUpload) -> UploadNoteOutput:

    core = NotesCore.from_request()
    title = uploaded_file.filename
    text = uploaded_file.stream.read().decode('utf-8')

    # TODO: ensure the file contains text, not binary data

    note_id = core.create(title=title, text=text)
    return UploadNoteOutput(ok=True, note_id=note_id)


# Current time: subscription -----------------------------------------

@schema.subscription.field('current_time')
def subscribe_current_time(root, info) -> str:
    # TODO: demonstrate authentication
    return Observable.from_iterable(poll_current_time())


def poll_current_time():
    while True:
        yield datetime.utcnow().strftime('%H:%M:%S')
        time.sleep(1)
