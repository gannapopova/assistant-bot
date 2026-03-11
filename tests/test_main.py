import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from unittest.mock import MagicMock
from colorama import Fore, init

from classes import AddressBook, Record, Birthday, Phone, Email, Address, Note, NoteBook
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
    add_email,
    add_address,
    search_contact,
    edit_contact,
    add_note, show_notes, find_note, edit_note, delete_note,
    add_tag, find_by_tag, show_notes_by_tags,
)
from helpers import parse_input

init(autoreset=True)


def make_book():
    """AddressBook with a mocked repository (no disk I/O)."""
    repo = MagicMock()
    repo.get_all.return_value = []
    return AddressBook(repository=repo)


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

    # --- Record to_dict / from_dict ---
    record.add_phone("1234567890")
    d = record.to_dict()
    assert d["name"] == "John"
    assert "1234567890" in d["phones"]
    assert d["birthday"] == "15.06.1990"

    restored = Record.from_dict(d)
    assert restored.name.value == "John"
    assert restored.find_phone("1234567890") == "1234567890"
    assert str(restored.birthday) == "15.06.1990"

    # --- Email validation ---
    e = Email("user@example.com")
    assert e.value == "user@example.com"

    for bad in ["notanemail", "missing@", "@nodomain.com", "no-at-sign"]:
        try:
            Email(bad)
            assert False, f"Should raise ValueError for: {bad}"
        except ValueError:
            pass

    # --- Address validation ---
    addr = Address(country="Ukraine", city="Kyiv", zip_code="01001")
    assert addr.city == "Kyiv"
    assert addr.zip_code == "01001"
    assert "Kyiv" in str(addr)
    assert "01001" in str(addr)

    try:
        Address(zip_code="ABC12")
        assert False, "Should raise ValueError for non-digit zip"
    except ValueError:
        pass

    # Empty address is falsy
    assert not Address()

    # Address to_dict / from_dict
    d = addr.to_dict()
    assert d["city"] == "Kyiv"
    restored_addr = Address.from_dict(d)
    assert restored_addr.city == "Kyiv"
    assert restored_addr.zip_code == "01001"

    # --- Record with email and address ---
    rec = Record("Test")
    rec.add_phone("1234567890")
    rec.add_email("test@example.com")
    rec.add_address(city="Lviv", street="Svobody", zip_code="79000")
    assert rec.email.value == "test@example.com"
    assert rec.address.city == "Lviv"
    assert "email: test@example.com" in str(rec)
    assert "address:" in str(rec)

    # to_dict includes email and address
    d = rec.to_dict()
    assert d["email"] == "test@example.com"
    assert d["address"]["city"] == "Lviv"

    # from_dict restores email and address
    restored = Record.from_dict(d)
    assert restored.email.value == "test@example.com"
    assert restored.address.city == "Lviv"

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
    book = make_book()
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

    empty_result = show_all([], make_book())
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
    fresh_book = make_book()

    add_contact(["Alice", "1111111111"], fresh_book)
    add_birthday(["Alice", today.strftime("%d.%m.1990")], fresh_book)

    in_3 = (today + timedelta(days=3)).strftime("%d.%m.1985")
    add_contact(["Bob", "2222222222"], fresh_book)
    add_birthday(["Bob", in_3], fresh_book)

    in_9 = (today + timedelta(days=9)).strftime("%d.%m.1985")
    add_contact(["Charlie", "3333333333"], fresh_book)
    add_birthday(["Charlie", in_9], fresh_book)

    add_contact(["Dave", "4444444444"], fresh_book)

    upcoming = fresh_book.get_upcoming_birthdays()
    names = [u["name"] for u in upcoming]
    assert "Alice" in names
    assert "Bob" in names
    assert "Charlie" not in names
    assert "Dave" not in names

    for u in upcoming:
        cong_date = datetime.strptime(u["congratulation_date"], "%d.%m.%Y").date()
        assert cong_date.weekday() < 5, f"{u['name']} congratulation falls on weekend"

    result = birthdays([], fresh_book)
    assert any(name in result for name in ["Alice", "Bob"])

    # birthdays with custom days argument
    result = birthdays(["30"], fresh_book)
    assert "Charlie" in result

    result = birthdays([], make_book())
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
    assert book.find("Bob") is None

    # --- find_phone_owner ---
    add_contact(["Alice", "9998887777"], book)
    result = find_phone_owner(["9998887777"], book)
    assert "Alice" in result

    result = find_phone_owner(["0000000000"], book)
    assert "not found" in result

    # --- add_email ---
    add_contact(["EmailUser", "1234567890"], book)
    result = add_email(["EmailUser", "user@test.com"], book)
    assert "Email added" in result
    assert book.find("EmailUser").email.value == "user@test.com"

    result = add_email(["EmailUser", "bad-email"], book)
    assert "Invalid arguments" in result

    result = add_email(["Unknown", "user@test.com"], book)
    assert "Contact not found" in result

    # --- add_address ---
    result = add_address(["EmailUser", "city=Kyiv", "zip_code=01001"], book)
    assert "Address added" in result
    assert book.find("EmailUser").address.city == "Kyiv"

    result = add_address(["EmailUser", "zip_code=BADZIP"], book)
    assert "Invalid arguments" in result

    result = add_address(["Unknown", "city=Kyiv"], book)
    assert "Contact not found" in result

    # --- search_contact ---
    result = search_contact(["EmailUser"], book)
    assert "EmailUser" in result

    result = search_contact(["user@test"], book)
    assert "EmailUser" in result

    result = search_contact(["nonexistent_xyz"], book)
    assert "No contacts found" in result

    # --- edit_contact ---
    result = edit_contact(["EmailUser", "email", "new@test.com"], book)
    assert "Contact updated" in result
    assert book.find("EmailUser").email.value == "new@test.com"

    result = edit_contact(["EmailUser", "birthday", "01.01.1990"], book)
    assert "Contact updated" in result

    result = edit_contact(["EmailUser", "unknown_field", "val"], book)
    assert "Invalid arguments" in result

    result = edit_contact(["Unknown", "email", "x@x.com"], book)
    assert "Contact not found" in result

    # --- Notes ---

    repo = MagicMock()
    repo.get_all.return_value = []
    notebook = NoteBook(repository=repo)

    # --- Note class ---
    note = Note("Hello world", tags=["python", "test"])
    assert note.text == "Hello world"
    assert "python" in note.tags
    assert len(note.id) == 36  # uuid4 format
    assert note.created_at is not None
    assert "[" in str(note)

    note.add_tag("newtag")
    assert "newtag" in note.tags
    note.add_tag("newtag")  # duplicate — should not add
    assert note.tags.count("newtag") == 1

    note.remove_tag("newtag")
    assert "newtag" not in note.tags

    d = note.to_dict()
    assert d["text"] == "Hello world"
    assert d["tags"] == ["python", "test"]
    restored_note = Note.from_dict(d)
    assert restored_note.id == note.id
    assert restored_note.text == note.text

    # --- add_note ---
    result = add_note(["My", "first", "note"], notebook)
    assert "Note added" in result
    assert len(notebook.data) == 1

    result = add_note([], notebook)
    assert "Invalid arguments" in result

    # --- show_notes ---
    result = show_notes([], notebook)
    assert "My first note" in result

    result = show_notes([], NoteBook(repository=MagicMock(get_all=lambda: [])))
    assert "No notes" in result

    # --- find_note ---
    add_note(["Another note about python"], notebook)
    result = find_note(["python"], notebook)
    assert "python" in result

    result = find_note(["nonexistent_xyz"], notebook)
    assert "No notes found" in result

    # --- add_tag ---
    note_id = list(notebook.data.keys())[0]
    prefix = note_id[:8]
    result = add_tag([prefix, "work"], notebook)
    assert "Tag 'work' added" in result
    assert "work" in notebook.data[note_id].tags

    result = add_tag(["badprefix"], notebook)
    assert "Invalid arguments" in result

    # --- find_by_tag ---
    result = find_by_tag(["work"], notebook)
    assert "My first note" in result

    result = find_by_tag(["notexist"], notebook)
    assert "No notes" in result

    # --- show_notes_by_tags ---
    result = show_notes_by_tags([], notebook)
    assert result  # returns something

    # --- edit_note ---
    result = edit_note([prefix, "Updated", "text"], notebook)
    assert "Note updated" in result
    assert notebook.data[note_id].text == "Updated text"

    result = edit_note([prefix], notebook)
    assert "Invalid arguments" in result

    # --- delete_note ---
    result = delete_note([prefix], notebook)
    assert "Note deleted" in result
    assert note_id not in notebook.data

    result = delete_note(["badprefix"], notebook)
    assert "not found" in result

    print(f"{Fore.GREEN}All tests passed successfully!")


if __name__ == "__main__":
    run_tests()
