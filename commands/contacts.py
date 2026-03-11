from colorama import Fore, init

from classes import AddressBook, Record
from helpers import input_error

init(autoreset=True)


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
        book.save_record(record)
    return f"{Fore.BLUE}{message}"


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Expected: change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    if record.edit_phone(old_phone, new_phone):
        book.save_record(record)
        return f"{Fore.BLUE}Phone updated."
    return f"{Fore.RED}Old phone not found."


@input_error
def add_email(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Expected: add-email <name> <email>")
    name, email = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_email(email)
    book.save_record(record)
    return f"{Fore.BLUE}Email added."


@input_error
def add_address(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Expected: add-address <name> <field=value> ...")
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    fields = {}
    for pair in args[1:]:
        if "=" not in pair:
            raise ValueError(f"Expected field=value format, got: {pair}")
        key, val = pair.split("=", 1)
        fields[key] = val
    record.add_address(**fields)
    book.save_record(record)
    return f"{Fore.BLUE}Address added."


@input_error
def search_contact(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Expected: search <query>")
    query = args[0].lower()
    results = []
    for record in book.data.values():
        if (
            query in record.name.value.lower()
            or any(query in p.value for p in record.phones)
            or (record.email and query in record.email.value.lower())
        ):
            results.append(str(record))
    if not results:
        return f"{Fore.YELLOW}No contacts found."
    return "\n".join(f"{Fore.BLUE}{r}" for r in results)


@input_error
def edit_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Expected: edit-contact <name> <field> <value>")
    name, field, value = args
    record = book.find(name)
    if not record:
        raise KeyError
    match field:
        case "email":
            record.edit_email(value)
        case "birthday":
            record.add_birthday(value)
        case _:
            raise ValueError(f"Unknown field: {field}. Use: email, birthday")
    book.save_record(record)
    return f"{Fore.BLUE}Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Expected: phone <name>")
    record = book.find(args[0])
    if not record:
        raise KeyError
    return f"{Fore.BLUE}{record}"


def show_all(args, book: AddressBook):
    if not book.data:
        return f"{Fore.BLUE}No contacts saved."
    return "\n".join(f"{Fore.BLUE}{r}" for r in book.data.values())


@input_error
def delete_contact(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Expected: delete-contact <name>")
    name = args[0]
    if book.delete(name):
        return f"{Fore.BLUE}Contact '{name}' deleted."
    raise KeyError


@input_error
def delete_phone(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Expected: delete-phone <name> <phone>")
    name, phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.remove_phone(phone)
    if not record.phones:
        book.delete(name)
        return f"{Fore.BLUE}Phone '{phone}' removed and contact '{name}' deleted (no phones left)."
    book.save_record(record)
    return f"{Fore.BLUE}Phone '{phone}' removed from {name}."


@input_error
def find_phone_owner(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Expected: find-owner <phone>")
    phone_to_find = args[0]
    for record in book.data.values():
        if record.find_phone(phone_to_find):
            return f"{Fore.BLUE}Phone {phone_to_find} belongs to {record.name}."
    return f"{Fore.RED}Phone {phone_to_find} not found."
