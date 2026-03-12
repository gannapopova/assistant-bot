import questionary
from colorama import Fore, init

from classes import AddressBook, NoteBook, Record

init(autoreset=True)


def _pause():
    input(f"\n{Fore.CYAN}Press Enter to continue...")


def _print(msg: str):
    print(f"\n{msg}")


# ─────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────

def run_menu(book: AddressBook, notebook: NoteBook):
    print(f"{Fore.MAGENTA}Welcome to the assistant bot!")
    while True:
        choice = questionary.select(
            "Main Menu:",
            choices=["Contacts", "Notes", "Exit"],
        ).ask()

        if choice is None or choice == "Exit":
            print(f"{Fore.MAGENTA}Good bye!")
            break
        elif choice == "Contacts":
            _contacts_menu(book)
        elif choice == "Notes":
            _notes_menu(notebook)


# ─────────────────────────────────────────────
# Contacts menu
# ─────────────────────────────────────────────

def _contacts_menu(book: AddressBook):
    actions = {
        "Add contact":       _wizard_add_contact,
        "Show all contacts": _show_all_contacts,
        "Find contact":      _find_contact,
        "Edit contact":      _wizard_edit_contact,
        "Delete contact":    _delete_contact,
        "Upcoming birthdays": _upcoming_birthdays,
    }
    while True:
        choice = questionary.select(
            "Contacts:",
            choices=list(actions.keys()) + ["Back"],
        ).ask()

        if choice is None or choice == "Back":
            break
        actions[choice](book)


# ─────────────────────────────────────────────
# Add contact wizard
# ─────────────────────────────────────────────

def _wizard_add_contact(book: AddressBook):
    name = questionary.text(
        "Name:",
        validate=lambda v: True if v.strip() else "Name cannot be empty",
    ).ask()
    if name is None:
        return
    name = name.strip()

    surname = questionary.text("Surname (optional):").ask()
    if surname is None:
        return

    phone = questionary.text(
        "Phone:",
        validate=lambda v: True if (v.isdigit() and len(v) == 10) else "Phone must be 10 digits",
    ).ask()
    if phone is None:
        return

    record = Record(name, surname=surname.strip() or None)
    book.add_record(record)
    record.add_phone(phone)
    book.save_record(record)

    email = questionary.text("Email (optional):").ask()
    if email:
        try:
            record.add_email(email)
            book.save_record(record)
        except ValueError as e:
            _print(f"{Fore.RED}{e}")

    birthday = questionary.text("Birthday (optional, DD.MM.YYYY):").ask()
    if birthday:
        try:
            record.add_birthday(birthday)
            book.save_record(record)
        except ValueError as e:
            _print(f"{Fore.RED}{e}")

    _print(f"{Fore.CYAN}Address (all fields optional, press Enter to skip):")
    addr_fields = {}
    for field, label in [
        ("country",   "Country"),
        ("city",      "City"),
        ("street",    "Street"),
        ("house",     "House"),
        ("apartment", "Apartment"),
        ("zip_code",  "Zip code"),
    ]:
        val = questionary.text(f"  {label}:").ask()
        if val:
            addr_fields[field] = val

    if addr_fields:
        try:
            record.add_address(**addr_fields)
            book.save_record(record)
        except ValueError as e:
            _print(f"{Fore.RED}{e}")

    _print(f"{Fore.BLUE}Contact saved:\n{record}")
    _pause()


# ─────────────────────────────────────────────
# Show all contacts
# ─────────────────────────────────────────────

def _show_all_contacts(book: AddressBook):
    if not book.data:
        _print(f"{Fore.BLUE}No contacts saved.")
    else:
        _print(f"{Fore.BLUE}" + "\n".join(str(r) for r in book.data.values()))
    _pause()


# ─────────────────────────────────────────────
# Find contact
# ─────────────────────────────────────────────

def _find_contact(book: AddressBook):
    query = questionary.text("Search query:").ask()
    if not query:
        return
    q = query.lower()
    results = [
        r for r in book.data.values()
        if (
            q in r.name.value.lower()
            or any(q in p.value for p in r.phones)
            or (r.email and q in r.email.value.lower())
        )
    ]
    if results:
        _print(f"{Fore.BLUE}" + "\n".join(str(r) for r in results))
    else:
        _print(f"{Fore.YELLOW}No contacts found.")
    _pause()


# ─────────────────────────────────────────────
# Edit contact wizard
# ─────────────────────────────────────────────

def _wizard_edit_contact(book: AddressBook):
    if not book.data:
        _print(f"{Fore.YELLOW}No contacts to edit.")
        _pause()
        return

    records = list(book.data.values())
    choices = [r.name.value for r in records] + ["Cancel"]
    selected_name = questionary.select("Select contact:", choices=choices).ask()
    if selected_name is None or selected_name == "Cancel":
        return

    record = next(r for r in records if r.name.value == selected_name)

    while True:
        choice = questionary.select(
            f"Edit {record.name.value}:",
            choices=["Phone", "Surname", "Email", "Birthday", "Address", "Done"],
        ).ask()

        if choice is None or choice == "Done":
            break
        elif choice == "Phone":
            _edit_phone(record, book)
        elif choice == "Surname":
            val = questionary.text(
                f"Surname (current: {record.surname or 'none'}):"
            ).ask()
            if val is not None:
                record.add_surname(val.strip() or None)
                book.save_record(record)
                _print(f"{Fore.BLUE}Surname updated.")
        elif choice == "Email":
            val = questionary.text(
                f"New email (current: {record.email or 'none'}):"
            ).ask()
            if val:
                try:
                    record.edit_email(val)
                    book.save_record(record)
                    _print(f"{Fore.BLUE}Email updated.")
                except ValueError as e:
                    _print(f"{Fore.RED}{e}")
        elif choice == "Birthday":
            val = questionary.text(
                f"New birthday DD.MM.YYYY (current: {record.birthday or 'none'}):"
            ).ask()
            if val:
                try:
                    record.add_birthday(val)
                    book.save_record(record)
                    _print(f"{Fore.BLUE}Birthday updated.")
                except ValueError as e:
                    _print(f"{Fore.RED}{e}")
        elif choice == "Address":
            _edit_address(record, book)


def _edit_phone(record: Record, book: AddressBook):
    phones = [p.value for p in record.phones]

    if not phones:
        phone = questionary.text(
            "No phones. Enter new phone:",
            validate=lambda v: True if (v.isdigit() and len(v) == 10) else "10 digits required",
        ).ask()
        if phone:
            record.add_phone(phone)
            book.save_record(record)
        return

    action = questionary.select(
        "Phone action:",
        choices=["Add new phone", "Change existing phone", "Delete phone", "Cancel"],
    ).ask()
    if action is None or action == "Cancel":
        return

    if action == "Add new phone":
        phone = questionary.text(
            "New phone:",
            validate=lambda v: True if (v.isdigit() and len(v) == 10) else "10 digits required",
        ).ask()
        if phone:
            try:
                record.add_phone(phone)
                book.save_record(record)
                _print(f"{Fore.BLUE}Phone added.")
            except ValueError as e:
                _print(f"{Fore.RED}{e}")

    elif action == "Change existing phone":
        old = questionary.select("Select phone to change:", choices=phones).ask()
        if old:
            new = questionary.text(
                "New phone:",
                validate=lambda v: True if (v.isdigit() and len(v) == 10) else "10 digits required",
            ).ask()
            if new:
                record.edit_phone(old, new)
                book.save_record(record)
                _print(f"{Fore.BLUE}Phone updated.")

    elif action == "Delete phone":
        old = questionary.select("Select phone to delete:", choices=phones).ask()
        if old:
            record.remove_phone(old)
            if not record.phones:
                book.delete_by_id(record.id)
                _print(f"{Fore.BLUE}Phone removed. Contact deleted (no phones left).")
                return
            book.save_record(record)
            _print(f"{Fore.BLUE}Phone removed.")


def _edit_address(record: Record, book: AddressBook):
    current = record.address
    _print(f"{Fore.CYAN}Current address: {current or 'none'}")
    addr_fields = {}
    for field, label in [
        ("country",   "Country"),
        ("city",      "City"),
        ("street",    "Street"),
        ("house",     "House"),
        ("apartment", "Apartment"),
        ("zip_code",  "Zip code"),
    ]:
        current_val = getattr(current, field, "") if current else ""
        val = questionary.text(f"  {label} (current: {current_val or 'empty'}):").ask()
        addr_fields[field] = val if val else current_val
    try:
        record.edit_address(**addr_fields)
        book.save_record(record)
        _print(f"{Fore.BLUE}Address updated.")
    except ValueError as e:
        _print(f"{Fore.RED}{e}")


# ─────────────────────────────────────────────
# Delete contact
# ─────────────────────────────────────────────

def _delete_contact(book: AddressBook):
    if not book.data:
        _print(f"{Fore.YELLOW}No contacts to delete.")
        _pause()
        return

    records = list(book.data.values())
    choices = [r.name.value for r in records] + ["Cancel"]
    selected_name = questionary.select("Select contact to delete:", choices=choices).ask()
    if selected_name is None or selected_name == "Cancel":
        return

    record = next(r for r in records if r.name.value == selected_name)
    confirmed = questionary.confirm(f"Delete '{selected_name}'?", default=False).ask()
    if confirmed:
        book.delete_by_id(record.id)
        _print(f"{Fore.BLUE}Contact '{selected_name}' deleted.")
        _pause()


# ─────────────────────────────────────────────
# Upcoming birthdays
# ─────────────────────────────────────────────

def _upcoming_birthdays(book: AddressBook):
    days_str = questionary.text(
        "Days ahead (default 7):",
        default="7",
        validate=lambda v: True if v.isdigit() and int(v) > 0 else "Enter a positive number",
    ).ask()
    if days_str is None:
        return
    days = int(days_str)
    upcoming = book.get_upcoming_birthdays(days=days)
    if upcoming:
        lines = [f"{u['name']}: {u['congratulation_date']}" for u in upcoming]
        _print(f"{Fore.BLUE}" + "\n".join(lines))
    else:
        _print(f"{Fore.BLUE}No birthdays in the next {days} days.")
    _pause()


# ─────────────────────────────────────────────
# Notes menu
# ─────────────────────────────────────────────

def _notes_menu(notebook: NoteBook):
    actions = {
        "Add note":           _wizard_add_note,
        "Show all notes":     _show_all_notes,
        "Find note":          _find_note,
        "Edit note":          _wizard_edit_note,
        "Delete note":        _delete_note,
        "Find by tag":        _find_by_tag,
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


# ─────────────────────────────────────────────
# Add note wizard
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Show all notes
# ─────────────────────────────────────────────

def _show_all_notes(notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        _print(f"{Fore.BLUE}No notes saved.")
    else:
        _print(f"{Fore.BLUE}" + "\n\n".join(str(n) for n in notes))
    _pause()


# ─────────────────────────────────────────────
# Find note
# ─────────────────────────────────────────────

def _find_note(notebook: NoteBook):
    query = questionary.text("Search query:").ask()
    if not query:
        return
    results = notebook.search(query)
    if results:
        _print(f"{Fore.BLUE}" + "\n\n".join(str(n) for n in results))
    else:
        _print(f"{Fore.YELLOW}No notes found.")
    _pause()


# ─────────────────────────────────────────────
# Edit note wizard
# ─────────────────────────────────────────────

def _wizard_edit_note(notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        _print(f"{Fore.YELLOW}No notes to edit.")
        _pause()
        return

    choices = [f"[{n.id[:8]}] {n.text[:50]}" for n in notes] + ["Cancel"]
    selected = questionary.select("Select note:", choices=choices).ask()
    if selected is None or selected == "Cancel":
        return

    note_id_prefix = selected[1:9]
    note = next((n for n in notes if n.id.startswith(note_id_prefix)), None)
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


# ─────────────────────────────────────────────
# Delete note
# ─────────────────────────────────────────────

def _delete_note(notebook: NoteBook):
    notes = notebook.get_all()
    if not notes:
        _print(f"{Fore.YELLOW}No notes to delete.")
        _pause()
        return

    choices = [f"[{n.id[:8]}] {n.text[:50]}" for n in notes] + ["Cancel"]
    selected = questionary.select("Select note to delete:", choices=choices).ask()
    if selected is None or selected == "Cancel":
        return

    note_id_prefix = selected[1:9]
    note = next((n for n in notes if n.id.startswith(note_id_prefix)), None)
    if not note:
        return

    confirmed = questionary.confirm(f"Delete this note?", default=False).ask()
    if confirmed:
        notebook.delete(note.id)
        _print(f"{Fore.BLUE}Note deleted.")
        _pause()


# ─────────────────────────────────────────────
# Find by tag
# ─────────────────────────────────────────────

def _find_by_tag(notebook: NoteBook):
    tag = questionary.text("Tag:").ask()
    if not tag:
        return
    results = notebook.find_by_tag(tag)
    if results:
        _print(f"{Fore.BLUE}" + "\n\n".join(str(n) for n in results))
    else:
        _print(f"{Fore.YELLOW}No notes with tag '{tag}'.")
    _pause()


# ─────────────────────────────────────────────
# Show sorted by tags
# ─────────────────────────────────────────────

def _show_sorted_by_tags(notebook: NoteBook):
    notes = notebook.get_all_sorted_by_tags()
    if not notes:
        _print(f"{Fore.BLUE}No notes saved.")
    else:
        _print(f"{Fore.BLUE}" + "\n\n".join(str(n) for n in notes))
    _pause()
