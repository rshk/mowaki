from ..schema.example import NotesTable
from .base import TableDB


class NotesDB(TableDB):
    table = NotesTable
