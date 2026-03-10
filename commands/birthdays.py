from colorama import Fore, init

from classes import AddressBook
from helpers import input_error

init(autoreset=True)


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Expected: add-birthday <name> <DD.MM.YYYY>")
    name, date = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(date)
    book.save_record(record)
    return f"{Fore.BLUE}Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Expected: show-birthday <name>")
    record = book.find(args[0])
    if not record:
        raise KeyError
    if not record.birthday:
        return f"{Fore.YELLOW}No birthday set for {args[0]}."
    return f"{Fore.BLUE}{args[0]}'s birthday: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days=days)
    if not upcoming:
        return f"{Fore.BLUE}No birthdays in the next {days} days."
    lines = [f"{Fore.BLUE}{u['name']}: {u['congratulation_date']}" for u in upcoming]
    return "\n".join(lines)
