import questionary
from colorama import Fore, init

from classes import AddressBook, Record

init(autoreset=True)


def _pause():
    input(f"\n{Fore.CYAN}Press Enter to continue...")


def _print(msg: str):
    print(f"\n{msg}")


# ─────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────

def run_menu(book: AddressBook):
    print(f"{Fore.MAGENTA}Welcome to the assistant bot!")
    while True:
        choice = questionary.select(
            "Main Menu:",
            choices=["Contacts", "Exit"],
        ).ask()

        if choice is None or choice == "Exit":
            print(f"{Fore.MAGENTA}Good bye!")
            break
        elif choice == "Contacts":
            _contacts_menu(book)


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

    phone = questionary.text(
        "Phone:",
        validate=lambda v: True if (v.isdigit() and len(v) == 10) else "Phone must be 10 digits",
    ).ask()
    if phone is None:
        return

    record = book.find(name)
    if record is None:
        record = Record(name)
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

    name = questionary.select(
        "Select contact:",
        choices=list(book.data.keys()) + ["Cancel"],
    ).ask()
    if name is None or name == "Cancel":
        return

    record = book.find(name)

    while True:
        choice = questionary.select(
            f"Edit {name}:",
            choices=["Phone", "Email", "Birthday", "Address", "Done"],
        ).ask()

        if choice is None or choice == "Done":
            break
        elif choice == "Phone":
            _edit_phone(record, book)
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
                book.delete(record.name.value)
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

    name = questionary.select(
        "Select contact to delete:",
        choices=list(book.data.keys()) + ["Cancel"],
    ).ask()
    if name is None or name == "Cancel":
        return

    confirmed = questionary.confirm(f"Delete '{name}'?", default=False).ask()
    if confirmed:
        book.delete(name)
        _print(f"{Fore.BLUE}Contact '{name}' deleted.")
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
