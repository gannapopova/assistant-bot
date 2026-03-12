import questionary
from colorama import Fore

from classes import AddressBook, Record
from helpers.tables import print_contacts_table_subset
from helpers.menu.utils import _pause, _print, table_view, CONTACT_SORTS


def contacts_menu(book: AddressBook):
    actions = {
        "Add contact":        _wizard_add_contact,
        "Show all contacts":  _show_all_contacts,
        "Find contact":       _find_contact,
        "Edit contact":       _wizard_edit_contact,
        "Delete contact":     _delete_contact,
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

    while True:
        email = questionary.text("Email (optional):").ask()
        if not email:
            break
        try:
            record.add_email(email)
            book.save_record(record)
            break
        except ValueError as e:
            _print(f"{Fore.RED}{e}")

    while True:
        birthday = questionary.text("Birthday (optional, DD.MM.YYYY):").ask()
        if not birthday:
            break
        try:
            record.add_birthday(birthday)
            book.save_record(record)
            break
        except ValueError as e:
            _print(f"{Fore.RED}{e}")

    _print(f"{Fore.CYAN}Address (all fields optional, press Enter to skip):")
    addr_fields = {}
    for field, label, validate_fn in [
        ("country",   "Country",   None),
        ("city",      "City",      None),
        ("street",    "Street",    None),
        ("house",     "House",     None),
        ("apartment", "Apartment", None),
        ("zip_code",  "Zip code",  lambda v: True if (not v or v.isdigit()) else "Zip code must contain digits only"),
    ]:
        kwargs = {"validate": validate_fn} if validate_fn else {}
        val = questionary.text(f"  {label}:", **kwargs).ask()
        if val:
            addr_fields[field] = val
    if addr_fields:
        record.add_address(**addr_fields)
        book.save_record(record)

    _print(f"{Fore.BLUE}Contact saved:\n{record}")
    _pause()


def _show_all_contacts(book: AddressBook):
    table_view(list(book.data.values()), print_contacts_table_subset, CONTACT_SORTS)


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
        table_view(results, print_contacts_table_subset, CONTACT_SORTS)
    else:
        _print(f"{Fore.YELLOW}No contacts found.")
        _pause()


def _wizard_edit_contact(book: AddressBook):
    if not book.data:
        _print(f"{Fore.YELLOW}No contacts to edit.")
        _pause()
        return

    records = list(book.data.values())
    choices = [
        questionary.Choice(title=f"{r.name.value}{' ' + r.surname.value if r.surname else ''}", value=r.id)
        for r in records
    ] + [questionary.Choice(title="Cancel", value=None)]
    selected_id = questionary.select("Select contact:", choices=choices).ask()
    if selected_id is None:
        return

    record = book.data[selected_id]

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
            while True:
                val = questionary.text(
                    f"New email (current: {record.email or 'none'}, leave empty to cancel):"
                ).ask()
                if not val:
                    break
                try:
                    record.edit_email(val)
                    book.save_record(record)
                    _print(f"{Fore.BLUE}Email updated.")
                    break
                except ValueError as e:
                    _print(f"{Fore.RED}{e}")
        elif choice == "Birthday":
            while True:
                val = questionary.text(
                    f"New birthday DD.MM.YYYY (current: {record.birthday or 'none'}, leave empty to cancel):"
                ).ask()
                if not val:
                    break
                try:
                    record.add_birthday(val)
                    book.save_record(record)
                    _print(f"{Fore.BLUE}Birthday updated.")
                    break
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
        while True:
            phone = questionary.text(
                "New phone:",
                validate=lambda v: True if (v.isdigit() and len(v) == 10) else "10 digits required",
            ).ask()
            if not phone:
                break
            try:
                record.add_phone(phone)
                book.save_record(record)
                _print(f"{Fore.BLUE}Phone added.")
                break
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
        if len(phones) == 1:
            _print(f"{Fore.YELLOW}Cannot remove the only phone. A contact must have at least one.")
            return
        old = questionary.select("Select phone to delete:", choices=phones).ask()
        if old:
            record.remove_phone(old)
            book.save_record(record)
            _print(f"{Fore.BLUE}Phone removed.")


def _edit_address(record: Record, book: AddressBook):
    current = record.address
    _print(f"{Fore.CYAN}Current address: {current or 'none'}")
    addr_fields = {}
    for field, label, validate_fn in [
        ("country",   "Country",   None),
        ("city",      "City",      None),
        ("street",    "Street",    None),
        ("house",     "House",     None),
        ("apartment", "Apartment", None),
        ("zip_code",  "Zip code",  lambda v: True if (not v or v.isdigit()) else "Zip code must contain digits only"),
    ]:
        current_val = getattr(current, field, "") if current else ""
        kwargs = {"validate": validate_fn} if validate_fn else {}
        val = questionary.text(f"  {label} (current: {current_val or 'empty'}):", **kwargs).ask()
        addr_fields[field] = val if val else current_val
    record.edit_address(**addr_fields)
    book.save_record(record)
    _print(f"{Fore.BLUE}Address updated.")


def _delete_contact(book: AddressBook):
    if not book.data:
        _print(f"{Fore.YELLOW}No contacts to delete.")
        _pause()
        return

    records = list(book.data.values())
    choices = [
        questionary.Choice(title=f"{r.name.value}{' ' + r.surname.value if r.surname else ''}", value=r.id)
        for r in records
    ] + [questionary.Choice(title="Cancel", value=None)]
    selected_id = questionary.select("Select contact to delete:", choices=choices).ask()
    if selected_id is None:
        return

    record = book.data[selected_id]
    confirmed = questionary.confirm(f"Delete '{record.name.value}'?", default=False).ask()
    if confirmed:
        book.delete_by_id(record.id)
        _print(f"{Fore.BLUE}Contact '{record.name.value}' deleted.")
        _pause()


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
