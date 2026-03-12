import uuid
from collections import UserDict
from datetime import datetime, timedelta

from .fields import Name, Surname, Phone, Birthday, Email, Address
from .repositories import ContactRepository


def _now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")


class Record:
    def __init__(self, name, surname: str = None, record_id: str = None, created_at: str = None, updated_at: str = None):
        self.id = record_id or str(uuid.uuid4())
        self.name = Name(name)
        self.surname = Surname(surname) if surname else None
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None
        self.created_at = created_at or _now()
        self.updated_at = updated_at or self.created_at

    def add_phone(self, phone_value):
        self.phones.append(Phone(phone_value))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def remove_phone(self, phone_value):
        self.phones = [p for p in self.phones if p.value != phone_value]

    def find_phone(self, phone_value):
        for p in self.phones:
            if p.value == phone_value:
                return p.value
        return None

    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def add_email(self, value: str):
        self.email = Email(value)

    def edit_email(self, value: str):
        self.email = Email(value)

    def add_address(self, **kwargs):
        self.address = Address(**kwargs)

    def edit_address(self, **kwargs):
        self.address = Address(**kwargs)

    def add_surname(self, value: str):
        self.surname = Surname(value) if value else None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name.value,
            "surname": self.surname.value if self.surname else None,
            "phones": [p.value for p in self.phones],
            "birthday": str(self.birthday) if self.birthday else None,
            "email": self.email.value if self.email else None,
            "address": self.address.to_dict() if self.address else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        record = cls(
            data["name"],
            surname=data.get("surname"),
            record_id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        for phone in data.get("phones", []):
            record.add_phone(phone)
        if data.get("birthday"):
            record.add_birthday(data["birthday"])
        if data.get("email"):
            record.add_email(data["email"])
        if data.get("address"):
            record.address = Address.from_dict(data["address"])
        return record

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones) or "no phones"
        full_name = f"{self.name} {self.surname}" if self.surname else str(self.name)
        parts = [f"{full_name}: {phones_str}"]
        if self.birthday:
            parts.append(f"birthday: {self.birthday}")
        if self.email:
            parts.append(f"email: {self.email}")
        if self.address:
            parts.append(f"address: {self.address}")
        return ", ".join(parts)


class AddressBook(UserDict):
    def __init__(self, repository: ContactRepository = None):
        super().__init__()
        self._repo = repository or ContactRepository()
        self._load()

    def _load(self):
        for contact in self._repo.get_all():
            record = Record.from_dict(contact)
            self.data[record.id] = record

    def add_record(self, record: Record):
        self.data[record.id] = record
        self._repo.upsert(record.to_dict())

    def find(self, name: str) -> Record | None:
        """Returns first record matching name (backward compat)."""
        for record in self.data.values():
            if record.name.value == name:
                return record
        return None

    def find_by_id(self, record_id: str) -> Record | None:
        return self.data.get(record_id)

    def find_all_by_name(self, name: str) -> list[Record]:
        return [r for r in self.data.values() if r.name.value == name]

    def delete_by_id(self, record_id: str) -> bool:
        if record_id in self.data:
            del self.data[record_id]
            self._repo.delete(record_id)
            return True
        return False

    def save_record(self, record: Record):
        record.updated_at = _now()
        self._repo.upsert(record.to_dict())

    def get_upcoming_birthdays(self, days: int = 7) -> list:
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = record.birthday.value
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            delta_days = (birthday_this_year - today).days

            if 0 <= delta_days <= days:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                })

        return upcoming
