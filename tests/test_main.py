import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from unittest.mock import MagicMock
from colorama import Fore, init

from classes import AddressBook, Record, Birthday, Phone, Email, Address, Note, NoteBook
from helpers import parse_input

init(autoreset=True)


def make_book():
    """AddressBook with a mocked repository (no disk I/O)."""
    repo = MagicMock()
    repo.get_all.return_value = []
    return AddressBook(repository=repo)


def find_note_by_prefix(prefix, notebook):
    for note in notebook.data.values():
        if note.id == prefix or note.id.startswith(prefix):
            return note
    return None


def test_field_validation():
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

    e = Email("user@example.com")
    assert e.value == "user@example.com"

    for bad in ["notanemail", "missing@", "@nodomain.com", "no-at-sign"]:
        try:
            Email(bad)
            assert False, f"Should raise ValueError for: {bad}"
        except ValueError:
            pass

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

    assert not Address()

    d = addr.to_dict()
    assert d["city"] == "Kyiv"
    restored_addr = Address.from_dict(d)
    assert restored_addr.city == "Kyiv"
    assert restored_addr.zip_code == "01001"


def test_record_serialization():
    rec_s = Record("John", surname="Doe")
    assert rec_s.surname.value == "Doe"
    assert "John Doe" in str(rec_s)
    rec_s.add_surname("Smith")
    assert rec_s.surname.value == "Smith"
    rec_s.add_surname(None)
    assert rec_s.surname is None
    d_s = rec_s.to_dict()
    assert d_s["surname"] is None
    rec_s2 = Record("John", surname="Doe")
    d_s2 = rec_s2.to_dict()
    assert d_s2["surname"] == "Doe"
    restored_s = Record.from_dict(d_s2)
    assert restored_s.surname.value == "Doe"

    record = Record("John")
    assert record.birthday is None
    record.add_birthday("15.06.1990")
    assert str(record.birthday) == "15.06.1990"
    assert "birthday: 15.06.1990" in str(record)

    record.add_phone("1234567890")
    d = record.to_dict()
    assert d["name"] == "John"
    assert "1234567890" in d["phones"]
    assert d["birthday"] == "15.06.1990"
    assert "id" in d
    assert "created_at" in d
    assert "updated_at" in d

    restored = Record.from_dict(d)
    assert restored.id == record.id
    assert restored.name.value == "John"
    assert restored.find_phone("1234567890") == "1234567890"
    assert str(restored.birthday) == "15.06.1990"
    assert restored.created_at == record.created_at

    rec = Record("Test")
    rec.add_phone("1234567890")
    rec.add_email("test@example.com")
    rec.add_address(city="Lviv", street="Svobody", zip_code="79000")
    assert rec.email.value == "test@example.com"
    assert rec.address.city == "Lviv"
    assert "email: test@example.com" in str(rec)
    assert "address:" in str(rec)

    d = rec.to_dict()
    assert d["email"] == "test@example.com"
    assert d["address"]["city"] == "Lviv"

    restored = Record.from_dict(d)
    assert restored.email.value == "test@example.com"
    assert restored.address.city == "Lviv"


def test_parse_input():
    cmd, args = parse_input("add John 1234567890")
    assert cmd == "add"
    assert args == ["John", "1234567890"]

    try:
        parse_input("   ")
        assert False, "Empty input should raise ValueError"
    except ValueError:
        pass


def test_address_book_crud():
    book = make_book()

    john = Record("John")
    john.add_phone("1234567890")
    book.add_record(john)
    book.save_record(john)
    assert book.find("John") is not None

    john.add_phone("5555555555")
    book.save_record(john)
    assert john.find_phone("1234567890") == "1234567890"
    assert john.find_phone("5555555555") == "5555555555"

    try:
        john.add_phone("123")
        assert False, "Should raise ValueError for short phone"
    except ValueError:
        pass

    john.edit_phone("1234567890", "1112223333")
    book.save_record(john)
    assert john.find_phone("1112223333") == "1112223333"
    assert john.find_phone("1234567890") is None

    assert book.find("Unknown") is None

    kate = Record("Kate")
    kate.add_phone("9998887777")
    book.add_record(kate)
    all_str = "\n".join(str(r) for r in book.data.values())
    assert "John" in all_str
    assert "Kate" in all_str
    assert not make_book().data

    john.add_birthday("15.06.1990")
    book.save_record(john)
    assert str(book.find("John").birthday) == "15.06.1990"

    try:
        john.add_birthday("wrong-format")
        assert False, "Should raise ValueError for wrong birthday format"
    except ValueError:
        pass

    assert str(john.birthday) == "15.06.1990"
    assert kate.birthday is None

    book.delete_by_id(kate.id)
    assert book.find("Kate") is None

    bob = Record("Bob")
    bob.add_phone("7776665555")
    book.add_record(bob)
    bob.remove_phone("7776665555")
    if not bob.phones:
        book.delete_by_id(bob.id)
    assert book.find("Bob") is None

    alice = Record("Alice")
    alice.add_phone("9998887777")
    book.add_record(alice)
    owner = next((r for r in book.data.values() if r.find_phone("9998887777")), None)
    assert owner is not None
    assert owner.name.value == "Alice"
    assert not any(r.find_phone("0000000000") for r in book.data.values())

    email_user = Record("EmailUser")
    email_user.add_phone("1234567890")
    book.add_record(email_user)
    email_user.add_email("user@test.com")
    book.save_record(email_user)
    assert book.find("EmailUser").email.value == "user@test.com"

    try:
        email_user.add_email("bad-email")
        assert False, "Should raise ValueError for invalid email"
    except ValueError:
        pass

    email_user.add_address(city="Kyiv", zip_code="01001")
    book.save_record(email_user)
    assert book.find("EmailUser").address.city == "Kyiv"

    try:
        email_user.add_address(zip_code="BADZIP")
        assert False, "Should raise ValueError for non-digit zip"
    except ValueError:
        pass

    results = [
        r for r in book.data.values()
        if "emailuser" in r.name.value.lower()
        or any("emailuser" in p.value for p in r.phones)
        or (r.email and "emailuser" in r.email.value.lower())
    ]
    assert any("EmailUser" in str(r) for r in results)

    results_by_email = [r for r in book.data.values() if r.email and "user@test" in r.email.value.lower()]
    assert any("EmailUser" in str(r) for r in results_by_email)

    assert not [r for r in book.data.values() if "nonexistent_xyz" in r.name.value.lower()]

    email_user.edit_email("new@test.com")
    book.save_record(email_user)
    assert book.find("EmailUser").email.value == "new@test.com"

    email_user.add_birthday("01.01.1990")
    book.save_record(email_user)
    assert str(book.find("EmailUser").birthday) == "01.01.1990"


def test_upcoming_birthdays():
    today = datetime.today().date()
    fresh_book = make_book()

    alice = Record("Alice")
    alice.add_phone("1111111111")
    alice.add_birthday(today.strftime("%d.%m.1990"))
    fresh_book.add_record(alice)

    bob = Record("Bob")
    bob.add_phone("2222222222")
    bob.add_birthday((today + timedelta(days=3)).strftime("%d.%m.1985"))
    fresh_book.add_record(bob)

    charlie = Record("Charlie")
    charlie.add_phone("3333333333")
    charlie.add_birthday((today + timedelta(days=9)).strftime("%d.%m.1985"))
    fresh_book.add_record(charlie)

    dave = Record("Dave")
    dave.add_phone("4444444444")
    fresh_book.add_record(dave)

    upcoming = fresh_book.get_upcoming_birthdays()
    names = [u["name"] for u in upcoming]
    assert "Alice" in names
    assert "Bob" in names
    assert "Charlie" not in names
    assert "Dave" not in names

    for u in upcoming:
        cong_date = datetime.strptime(u["congratulation_date"], "%d.%m.%Y").date()
        assert cong_date.weekday() < 5, f"{u['name']} congratulation falls on weekend"

    names_30 = [u["name"] for u in fresh_book.get_upcoming_birthdays(days=30)]
    assert "Charlie" in names_30

    assert make_book().get_upcoming_birthdays() == []


def test_notes():
    repo = MagicMock()
    repo.get_all.return_value = []
    notebook = NoteBook(repository=repo)

    note = Note("Hello world", tags=["python", "test"])
    assert note.text == "Hello world"
    assert "python" in note.tags
    assert len(note.id) == 36
    assert note.created_at is not None
    assert "[" in str(note)

    note.add_tag("newtag")
    assert "newtag" in note.tags
    note.add_tag("newtag")
    assert note.tags.count("newtag") == 1

    note.remove_tag("newtag")
    assert "newtag" not in note.tags

    d = note.to_dict()
    assert d["text"] == "Hello world"
    assert d["tags"] == ["python", "test"]
    restored_note = Note.from_dict(d)
    assert restored_note.id == note.id
    assert restored_note.text == note.text

    notebook.add("My first note")
    assert len(notebook.data) == 1

    try:
        notebook.add("")
    except Exception:
        pass

    assert any("My first note" in n.text for n in notebook.get_all())
    assert not NoteBook(repository=MagicMock(get_all=lambda: [])).get_all()

    notebook.add("Another note about python")
    assert any("python" in n.text for n in notebook.search("python"))
    assert not notebook.search("nonexistent_xyz")

    note_id = list(notebook.data.keys())[0]
    prefix = note_id[:8]
    target = find_note_by_prefix(prefix, notebook)
    assert target is not None
    target.add_tag("work")
    notebook.save_note(target)
    assert "work" in notebook.data[note_id].tags

    assert find_note_by_prefix("badprefix_xyz_000", notebook) is None

    assert any("My first note" in n.text for n in notebook.find_by_tag("work"))
    assert not notebook.find_by_tag("notexist")

    assert notebook.get_all_sorted_by_tags()

    target.text = "Updated text"
    notebook.save_note(target)
    assert notebook.data[note_id].text == "Updated text"

    notebook.delete(note_id)
    assert note_id not in notebook.data
    assert find_note_by_prefix("badprefix", notebook) is None


def run_tests():
    test_field_validation()
    test_record_serialization()
    test_parse_input()
    test_address_book_crud()
    test_upcoming_birthdays()
    test_notes()
    print(f"{Fore.GREEN}All tests passed successfully!")


if __name__ == "__main__":
    run_tests()
