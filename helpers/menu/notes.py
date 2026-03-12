import questionary
from colorama import Fore

from classes import NoteBook
from helpers.tables import print_notes_table
from helpers.menu.utils import _pause, _print, table_view, NOTE_SORTS


def notes_menu(notebook: NoteBook):
    actions = {
        "Add note":            _wizard_add_note,
        "Show all notes":      _show_all_notes,
        "Find note":           _find_note,
        "Edit note":           _wizard_edit_note,
        "Delete note":         _delete_note,
        "Find by tag":         _find_by_tag,
        "Show sorted by tags": _show_sorted_by_tags,
    }
    while True:
        choice = questionary.select(
            "Notes:",
            choices=list(actions.keys()) + ["Back"],
        ).ask()

        if choice is None or choice == "Back":
            break
        actions[choice](notebook)


def _wizard_add_note(notebook: NoteBook):
    text = questionary.text(
        "Note text:",
        validate=lambda v: True if v.strip() else "Text cannot be empty",
    ).ask()
    if text is None:
        return

    tags_input = questionary.text("Tags (optional, comma-separated):").ask()
    tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()] if tags_input else []

    note = notebook.add(text.strip(), tags)
    _print(f"{Fore.BLUE}Note saved:\n{note}")
    _pause()


def _show_all_notes(notebook: NoteBook):
    table_view(notebook.get_all(), print_notes_table, NOTE_SORTS)


def _find_note(notebook: NoteBook):
    query = questionary.text("Search query:").ask()
    if not query:
        return
    results = notebook.search(query)
    if results:
        table_view(results, print_notes_table, NOTE_SORTS)
    else:
        _print(f"{Fore.YELLOW}No notes found.")
        _pause()


def _wizard_edit_note(notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        _print(f"{Fore.YELLOW}No notes to edit.")
        _pause()
        return

    choices = [
        questionary.Choice(title=f"[{n.id[:8]}] {n.text[:50]}", value=n.id)
        for n in notes
    ] + ["Cancel"]
    selected_id = questionary.select("Select note:", choices=choices).ask()
    if selected_id is None or selected_id == "Cancel":
        return

    note = next((n for n in notes if n.id == selected_id), None)
    if not note:
        return

    while True:
        choice = questionary.select(
            f"Edit note [{note.id[:8]}]:",
            choices=["Edit text", "Edit tags", "Done"],
        ).ask()

        if choice is None or choice == "Done":
            break
        elif choice == "Edit text":
            new_text = questionary.text(
                "New text:",
                default=note.text,
                validate=lambda v: True if v.strip() else "Text cannot be empty",
            ).ask()
            if new_text:
                note.text = new_text.strip()
                notebook.save_note(note)
                _print(f"{Fore.BLUE}Text updated.")
        elif choice == "Edit tags":
            _edit_note_tags(note, notebook)


def _edit_note_tags(note, notebook: NoteBook):
    while True:
        action = questionary.select(
            f"Tags: {note.tags or 'none'}",
            choices=["Add tag", "Remove tag", "Done"],
        ).ask()

        if action is None or action == "Done":
            break
        elif action == "Add tag":
            tag = questionary.text("New tag:").ask()
            if tag:
                note.add_tag(tag)
                notebook.save_note(note)
                _print(f"{Fore.BLUE}Tag added.")
        elif action == "Remove tag":
            if not note.tags:
                _print(f"{Fore.YELLOW}No tags to remove.")
                continue
            tag = questionary.select("Select tag to remove:", choices=note.tags + ["Cancel"]).ask()
            if tag and tag != "Cancel":
                note.remove_tag(tag)
                notebook.save_note(note)
                _print(f"{Fore.BLUE}Tag removed.")


def _delete_note(notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        _print(f"{Fore.YELLOW}No notes to delete.")
        _pause()
        return

    choices = [
        questionary.Choice(title=f"[{n.id[:8]}] {n.text[:50]}", value=n.id)
        for n in notes
    ] + ["Cancel"]
    selected_id = questionary.select("Select note to delete:", choices=choices).ask()
    if selected_id is None or selected_id == "Cancel":
        return

    note = next((n for n in notes if n.id == selected_id), None)
    if not note:
        return

    confirmed = questionary.confirm("Delete this note?", default=False).ask()
    if confirmed:
        notebook.delete(note.id)
        _print(f"{Fore.BLUE}Note deleted.")
        _pause()


def _find_by_tag(notebook: NoteBook):
    tag = questionary.text("Tag:").ask()
    if not tag:
        return
    results = notebook.find_by_tag(tag)
    if results:
        table_view(results, print_notes_table, NOTE_SORTS)
    else:
        _print(f"{Fore.YELLOW}No notes with tag '{tag}'.")
        _pause()


def _show_sorted_by_tags(notebook: NoteBook):
    table_view(notebook.get_all(), print_notes_table, NOTE_SORTS, default_sort_idx=3)
