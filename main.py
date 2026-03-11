from classes import AddressBook, NoteBook
from helpers import run_menu


def main():
    book = AddressBook()
    notebook = NoteBook()
    run_menu(book, notebook)


if __name__ == "__main__":
    main()
