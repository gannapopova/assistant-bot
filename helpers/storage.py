import os
import pickle
from colorama import Fore, init
from pathlib import Path

from classes import AddressBook

STORAGE_DIR = Path.home() / ".assistant-bot"
STORAGE_DIR.mkdir(exist_ok=True)
STORAGE_FILE = STORAGE_DIR / "addressbook.pkl"

init(autoreset=True)

def save_data(book: AddressBook, filename: Path = STORAGE_FILE):
    print(f"{Fore.YELLOW}Processing data storage...")
    tmp = filename.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(book, f)
    if filename.exists():
        filename.replace(filename.with_suffix(".bak"))
        print(f"{Fore.YELLOW}Backup was created.")
    os.replace(tmp, filename)
    print(f"{Fore.YELLOW}Data was successfully saved.")


def load_data(filename: Path = STORAGE_FILE) -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
