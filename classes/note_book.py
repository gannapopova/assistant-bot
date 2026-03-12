from collections import UserDict
from datetime import datetime

from .notes import Note
from .repositories import NoteRepository


def _now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")


class NoteBook(UserDict):
    def __init__(self, repository: NoteRepository = None):
        super().__init__()
        self._repo = repository or NoteRepository()
        self._load()

    def _load(self):
        for note_data in self._repo.get_all():
            note = Note.from_dict(note_data)
            self.data[note.id] = note

    def add(self, text: str, tags: list[str] = None) -> Note:
        note = Note(text=text, tags=tags or [])
        self.data[note.id] = note
        self._repo.upsert(note.to_dict())
        return note

    def find_by_id(self, note_id: str) -> Note | None:
        return self.data.get(note_id)

    def delete(self, note_id: str) -> bool:
        if note_id in self.data:
            del self.data[note_id]
            self._repo.delete(note_id)
            return True
        return False

    def save_note(self, note: Note):
        note.updated_at = _now()
        self._repo.upsert(note.to_dict())

    def get_all(self) -> list[Note]:
        return list(self.data.values())

    def search(self, query: str) -> list[Note]:
        q = query.lower()
        return [n for n in self.data.values() if q in n.text.lower()]

    def find_by_tag(self, tag: str) -> list[Note]:
        tag = tag.strip().lower()
        return [n for n in self.data.values() if tag in n.tags]

    def get_all_sorted_by_tags(self) -> list[Note]:
        def sort_key(note: Note):
            return note.tags[0] if note.tags else "\xff"  # notes without tags go last
        return sorted(self.data.values(), key=sort_key)
