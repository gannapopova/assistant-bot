import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from colorama import Fore, init

from classes import AddressBook, Record, Birthday, Phone
from commands import (
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


def run_tests():
    # --- Birthday field validation ---
    b = Birthday("15.06.1990")
    assert str(b) == "15.06.1990"

    try:
        Birthday("1990-06-15")
        assert False, "Should raise ValueError for wrong format"
    except ValueError as e:
        assert "DD.MM.YYYY" in str(e)

    try:
        Birthday("31.02.2000")
        assert False, "Should raise ValueError for invalid date"
    except ValueError:
        pass

    # --- Phone field validation ---
    p = Phone("1234567890")
    assert str(p) == "1234567890"

    try:
        Phone("123")
        assert False, "Should raise ValueError for short phone"
    except ValueError:
        pass

    try:
        Phone("12345678ab")
        assert False, "Should raise ValueError for non-digit phone"
    except ValueError:
        pass

    # --- Record.add_birthday ---
    record = Record("John")
    assert record.birthday is None
    record.add_birthday("15.06.1990")
    assert str(record.birthday) == "15.06.1990"
    assert "birthday: 15.06.1990" in str(record)

    # --- parse_input ---
    cmd, args = parse_input("add John 1234567890")
    assert cmd == "add"
    assert args == ["John", "1234567890"]

    try:
        parse_input("   ")
        assert False, "Empty input should raise ValueError"
    except ValueError:
        pass

    # --- add_contact ---
    book = AddressBook()
    result = add_contact(["John", "1234567890"], book)
    assert "Contact added" in result
    result = add_contact(["John", "5555555555"], book)
    assert "Contact updated" in result
    john = book.find("John")
    assert john.find_phone("1234567890") == "1234567890"
    assert john.find_phone("5555555555") == "5555555555"

    result = add_contact(["Mike", "123"], book)
    assert "Invalid arguments" in result

    result = add_contact(["OnlyName"], book)
    assert "Invalid arguments" in result

    # --- change_contact ---
    result = change_contact(["John", "1234567890", "1112223333"], book)
    assert "Phone updated" in result
    assert john.find_phone("1112223333") == "1112223333"
    assert john.find_phone("1234567890") is None

    result = change_contact(["Unknown", "0000000000", "1111111111"], book)
    assert "Contact not found" in result

    result = change_contact(["OnlyName"], book)
    assert "Invalid arguments" in result

    # --- show_phone ---
    result = show_phone(["John"], book)
    assert "1112223333" in result
    assert "5555555555" in result

    result = show_phone(["Unknown"], book)
    assert "Contact not found" in result

    result = show_phone([], book)
    assert "Invalid arguments" in result

    # --- show_all ---
    add_contact(["Kate", "9998887777"], book)
    result = show_all([], book)
    assert "John" in result
    assert "Kate" in result

    empty_result = show_all([], AddressBook())
    assert "No contacts saved" in empty_result

    # --- add_birthday command ---
    result = add_birthday(["John", "15.06.1990"], book)
    assert "Birthday added" in result
    assert str(book.find("John").birthday) == "15.06.1990"

    result = add_birthday(["Unknown", "15.06.1990"], book)
    assert "Contact not found" in result

    result = add_birthday(["John", "wrong-format"], book)
    assert "Invalid arguments" in result

    result = add_birthday(["OnlyName"], book)
    assert "Invalid arguments" in result

    # --- show_birthday command ---
    result = show_birthday(["John"], book)
    assert "15.06.1990" in result

    result = show_birthday(["Kate"], book)
    assert "No birthday set" in result

    result = show_birthday(["Unknown"], book)
    assert "Contact not found" in result

    result = show_birthday([], book)
    assert "Invalid arguments" in result

    # --- get_upcoming_birthdays / birthdays command ---
    today = datetime.today().date()
    fresh_book = AddressBook()

    # Birthday today
    add_contact(["Alice", "1111111111"], fresh_book)
    add_birthday(["Alice", today.strftime("%d.%m.1990")], fresh_book)

    # Birthday in 3 days
    in_3 = (today + timedelta(days=3)).strftime("%d.%m.1985")
    add_contact(["Bob", "2222222222"], fresh_book)
    add_birthday(["Bob", in_3], fresh_book)

    # Birthday in 9 days (outside window)
    in_9 = (today + timedelta(days=9)).strftime("%d.%m.1985")
    add_contact(["Charlie", "3333333333"], fresh_book)
    add_birthday(["Charlie", in_9], fresh_book)

    # Contact with no birthday
    add_contact(["Dave", "4444444444"], fresh_book)

    upcoming = fresh_book.get_upcoming_birthdays()
    names = [u["name"] for u in upcoming]
    assert "Alice" in names
    assert "Bob" in names
    assert "Charlie" not in names
    assert "Dave" not in names

    # All congratulation dates must be weekdays (Mon–Fri)
    for u in upcoming:
        cong_date = datetime.strptime(u["congratulation_date"], "%d.%m.%Y").date()
        assert cong_date.weekday() < 5, f"{u['name']} congratulation falls on weekend"

    result = birthdays([], fresh_book)
    assert any(name in result for name in ["Alice", "Bob"])

    result = birthdays([], AddressBook())
    assert "No birthdays" in result

    # --- delete_contact ---
    result = delete_contact(["Kate"], book)
    assert "deleted" in result
    assert book.find("Kate") is None

    result = delete_contact(["Unknown"], book)
    assert "Contact not found" in result

    # --- delete_phone ---
    add_contact(["Bob", "7776665555"], book)
    result = delete_phone(["Bob", "7776665555"], book)
    assert "deleted" in result
    assert book.find("Bob") is None  # auto-deleted when no phones left

    # --- find_phone_owner ---
    add_contact(["Alice", "9998887777"], book)
    result = find_phone_owner(["9998887777"], book)
    assert "Alice" in result

    result = find_phone_owner(["0000000000"], book)
    assert "not found" in result

    # --- save_data / load_data ---
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    bak_path = tmp_path.with_suffix(".bak")

    try:
        # basic save and load
        save_book = AddressBook()
        add_contact(["SavedUser", "1231231234"], save_book)
        add_birthday(["SavedUser", "01.01.1990"], save_book)
        save_data(save_book, tmp_path)

        loaded_book = load_data(tmp_path)
        loaded = loaded_book.find("SavedUser")
        assert loaded is not None
        assert loaded.find_phone("1231231234") == "1231231234"
        assert str(loaded.birthday) == "01.01.1990"

        # second save creates .bak with previous state
        save_book_v2 = AddressBook()
        add_contact(["NewUser", "9879879870"], save_book_v2)
        save_data(save_book_v2, tmp_path)

        assert bak_path.exists(), ".bak file should be created on second save"
        bak_book = load_data(bak_path)
        assert bak_book.find("SavedUser") is not None, ".bak should contain previous state"
        assert bak_book.find("NewUser") is None

        # main file has new state
        current_book = load_data(tmp_path)
        assert current_book.find("NewUser") is not None
        assert current_book.find("SavedUser") is None

        # no leftover .tmp file after save
        assert not tmp_path.with_suffix(".tmp").exists(), ".tmp should be cleaned up after save"

    finally:
        tmp_path.unlink(missing_ok=True)
        bak_path.unlink(missing_ok=True)

    # load from non-existent file returns empty AddressBook
    empty = load_data(Path("/nonexistent/path.pkl"))
    assert isinstance(empty, AddressBook)
    assert len(empty.data) == 0

    # --- try/finally: save_data called on unexpected crash ---
    import main as main_module
    from unittest.mock import patch

    for exception in (RuntimeError("crash"), KeyboardInterrupt()):
        saved = []

        def capture_save(book, *_args, **_kwargs):
            saved.append(book)

        test_book = AddressBook()
        add_contact(["TestUser", "1234567890"], test_book)

        with patch("builtins.input", side_effect=exception), \
             patch.object(main_module, "load_data", return_value=test_book), \
             patch.object(main_module, "save_data", side_effect=capture_save):
            try:
                main_module.main()
            except type(exception):
                pass

        assert len(saved) == 1, f"save_data must be called on {type(exception).__name__}"
        assert saved[0].find("TestUser") is not None

    print(f"{Fore.GREEN}All tests passed successfully!")


if __name__ == "__main__":
    run_tests()
