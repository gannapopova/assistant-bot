import questionary
from colorama import Fore, init

from classes import AddressBook, NoteBook
from helpers.menu.contacts import contacts_menu
from helpers.menu.notes import notes_menu

init(autoreset=True)


def run_menu(book: AddressBook, notebook: NoteBook):
    print(f"{Fore.MAGENTA}Welcome to the assistant bot!")
    try:
        while True:
            choice = questionary.select(
                "Main Menu:",
                choices=["Contacts", "Notes", "Exit"],
            ).ask()

            if choice is None or choice == "Exit":
                break
            elif choice == "Contacts":
                contacts_menu(book)
            elif choice == "Notes":
                notes_menu(notebook)
    except KeyboardInterrupt:
        pass
    print(f"\n{Fore.MAGENTA}Good bye!")
