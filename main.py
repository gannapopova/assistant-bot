from colorama import Fore, init

from classes import AddressBook
from commands import (
    hello,
    add_contact,
    change_contact,
    show_phone,
    show_all,
    add_birthday,
    show_birthday,
    birthdays,
    delete_contact,
    delete_phone,
    find_phone_owner,
)
from helpers import parse_input, save_data, load_data

init(autoreset=True)

COMMANDS = {
    "hello":          hello,
    "add":            add_contact,
    "change":         change_contact,
    "phone":          show_phone,
    "all":            show_all,
    "add-birthday":   add_birthday,
    "show-birthday":  show_birthday,
    "birthdays":      birthdays,
    "delete-contact": delete_contact,
    "delete-phone":   delete_phone,
    "find-owner":     find_phone_owner,
}


def main():
    book = load_data()
    print(f"{Fore.MAGENTA}Welcome to the assistant bot!")

    try:
        while True:
            user_input = input(f"{Fore.GREEN}Enter a command: ")
            try:
                command, args = parse_input(user_input)
            except ValueError:
                print(f"{Fore.RED}Please enter a command.")
                continue

            if command in ["close", "exit"]:
                print(f"{Fore.MAGENTA}Good bye!")
                break

            handler = COMMANDS.get(command)
            if handler:
                print(handler(args, book))
            else:
                print(f"{Fore.RED}Invalid command.")
    finally:
        save_data(book)


if __name__ == "__main__":
    main()
