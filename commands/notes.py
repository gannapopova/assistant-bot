from colorama import Fore, init

from classes import NoteBook
from helpers import input_error

init(autoreset=True)


@input_error
def add_note(args, notebook: NoteBook):
    if not args:
        raise ValueError("Expected: add-note <text>")
    text = " ".join(args)
    note = notebook.add(text)
    return f"{Fore.BLUE}Note added: [{note.id[:8]}]"


@input_error
def show_notes(args, notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        return f"{Fore.BLUE}No notes saved."
    return "\n\n".join(f"{Fore.BLUE}{n}" for n in notes)


@input_error
def find_note(args, notebook: NoteBook):
    if not args:
        raise ValueError("Expected: find-note <query>")
    query = " ".join(args)
    results = notebook.search(query)
    if not results:
        return f"{Fore.YELLOW}No notes found."
    return "\n\n".join(f"{Fore.BLUE}{n}" for n in results)


@input_error
def edit_note(args, notebook: NoteBook):
    if len(args) < 2:
        raise ValueError("Expected: edit-note <id> <new text>")
    note_id_prefix, *text_parts = args
    note = _find_by_prefix(note_id_prefix, notebook)
    if not note:
        return f"{Fore.RED}Note not found."
    note.text = " ".join(text_parts)
    notebook.save_note(note)
    return f"{Fore.BLUE}Note updated."


@input_error
def delete_note(args, notebook: NoteBook):
    if not args:
        raise ValueError("Expected: delete-note <id>")
    note = _find_by_prefix(args[0], notebook)
    if not note:
        return f"{Fore.RED}Note not found."
    notebook.delete(note.id)
    return f"{Fore.BLUE}Note deleted."


@input_error
def add_tag(args, notebook: NoteBook):
    if len(args) < 2:
        raise ValueError("Expected: add-tag <id> <tag>")
    note_id_prefix, tag = args[0], args[1]
    note = _find_by_prefix(note_id_prefix, notebook)
    if not note:
        return f"{Fore.RED}Note not found."
    note.add_tag(tag)
    notebook.save_note(note)
    return f"{Fore.BLUE}Tag '{tag}' added."


@input_error
def find_by_tag(args, notebook: NoteBook):
    if not args:
        raise ValueError("Expected: find-by-tag <tag>")
    results = notebook.find_by_tag(args[0])
    if not results:
        return f"{Fore.YELLOW}No notes with tag '{args[0]}'."
    return "\n\n".join(f"{Fore.BLUE}{n}" for n in results)


@input_error
def show_notes_by_tags(args, notebook: NoteBook):
    notes = notebook.get_all_sorted_by_tags()
    if not notes:
        return f"{Fore.BLUE}No notes saved."
    return "\n\n".join(f"{Fore.BLUE}{n}" for n in notes)


def _find_by_prefix(prefix: str, notebook: NoteBook):
    """Find note by full id or first 8 chars prefix."""
    for note in notebook.data.values():
        if note.id == prefix or note.id.startswith(prefix):
            return note
    return None
