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
        return f"{Fore.BLUE}Phone updated."
    return f"{Fore.RED}Old phone not found."


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
