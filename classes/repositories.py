import json
from pathlib import Path

STORAGE_DIR = Path.home() / ".assistant-bot"
STORAGE_DIR.mkdir(exist_ok=True)


class ContactRepository:
    def __init__(self, filepath: Path = STORAGE_DIR / "contacts.json"):
        self._filepath = filepath

    def get_all(self) -> list[dict]:
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_all(self, contacts: list[dict]):
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)

    def upsert(self, contact: dict):
        contacts = self.get_all()
        for i, c in enumerate(contacts):
            if c.get("id") == contact["id"]:
                contacts[i] = contact
                self.save_all(contacts)
                return
        contacts.append(contact)
        self.save_all(contacts)

    def delete(self, record_id: str) -> bool:
        contacts = self.get_all()
        filtered = [c for c in contacts if c.get("id") != record_id]
        if len(filtered) == len(contacts):
            return False
        self.save_all(filtered)
        return True


class NoteRepository:
    def __init__(self, filepath: Path = STORAGE_DIR / "notes.json"):
        self._filepath = filepath

    def get_all(self) -> list[dict]:
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_all(self, notes: list[dict]):
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

    def upsert(self, note: dict):
        notes = self.get_all()
        for i, n in enumerate(notes):
            if n["id"] == note["id"]:
                notes[i] = note
                self.save_all(notes)
                return
        notes.append(note)
        self.save_all(notes)

    def delete(self, note_id: str) -> bool:
        notes = self.get_all()
        filtered = [n for n in notes if n["id"] != note_id]
        if len(filtered) == len(notes):
            return False
        self.save_all(filtered)
        return True
