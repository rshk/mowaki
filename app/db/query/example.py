import itertools
from collections import namedtuple

Note = namedtuple('Note', 'id,title,body')

note_idx_seq = itertools.count(1)

NOTES = {}


def list_notes():
    return [note for idx, note in sorted(NOTES.items())]


def get_note(idx):
    return NOTES.get(idx)


def create_note(title, body):
    idx = next(note_idx_seq)
    note = Note(
        id=idx,
        title=title,
        body=body)
    NOTES[idx] = note
    return idx


def update_note(idx, title=None, body=None):
    try:
        note = NOTES[idx]
    except KeyError:
        return

    updates = {}

    if title is not None:
        updates['title'] = title
    if body is not None:
        updates['body'] = body

    NOTES[idx] = note._replace(**updates)


def delete_note(idx):
    NOTES.pop(idx, None)


create_note('Hello world', 'This is the first note')
create_note('Second note', 'This is the second note')
