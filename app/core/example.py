from app.db.query.example import NotesDB

from .base import BaseCore
from .exceptions import AuthorizationError, ValidationError

# Allow anonymous users to create notes
EVERYONE_CAN_CREATE_NOTES = True


class NotesCore(BaseCore):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._notes_db = NotesDB()

    def get(self, uid):
        note = self._notes_db.get(id=uid)

        if not self.can_access_note(note):
            raise AuthorizationError('Cannot get this note')

        return note

    def list(self):

        if not self.can_list_notes():
            raise AuthorizationError('Cannot list notes')

        return self._notes_db.list()

    def create(self, title=None, text=None):

        if not self.can_create_note():
            raise AuthorizationError('Cannot create notes')

        title = (title or '').strip()
        text = (text or '').strip()

        if not title.strip():
            raise ValidationError('Title must not be empty')

        return self._notes_db.create(title=title, text=text)

    def update(self, note, title=None, text=None):

        if not self.can_update_note(note):
            raise AuthorizationError('Cannot update note')

        updates = {}

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError('Title must not be empty')
            updates['title'] = title.strip()

        if text is not None:
            updates['text'] = text.strip()

        self._notes_db.update(id=note.id, **updates)

    def delete(self, note):

        if not self.can_delete_note(note):
            raise AuthorizationError('Cannot delete note')

        self._notes_db.delete(id=note.id)

    # Authorization --------------------------------------------------

    def can_access_note(self, note):
        auth = self.get_auth_info()

        if auth.is_superuser():
            return True

        return True

    def can_list_notes(self):
        auth = self.get_auth_info()

        if auth.is_superuser():
            return True

        return True

    def can_create_note(self):
        auth = self.get_auth_info()

        if auth.is_superuser():
            return True

        if auth.is_authenticated():
            return True

        if EVERYONE_CAN_CREATE_NOTES:
            return True

        return False

    def can_update_note(self, note):
        auth = self.get_auth_info()

        if auth.is_superuser():
            return True

        if auth.is_authenticated():
            return True

        if EVERYONE_CAN_CREATE_NOTES:
            return True

        return False

    def can_delete_note(self, note):
        auth = self.get_auth_info()

        if auth.is_superuser():
            return True

        if auth.is_authenticated():
            return True

        if EVERYONE_CAN_CREATE_NOTES:
            return True

        return False
