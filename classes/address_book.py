from collections import UserDict
from datetime import datetime, timedelta

from .fields import Name, Phone, Birthday, Email, Address
from .repositories import ContactRepository


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

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

    def to_dict(self) -> dict:
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": str(self.birthday) if self.birthday else None,
            "email": self.email.value if self.email else None,
            "address": self.address.to_dict() if self.address else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        record = cls(data["name"])
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
        parts = [f"{self.name}: {phones_str}"]
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
            self.data[record.name.value] = record

    def add_record(self, record: Record):
        self.data[record.name.value] = record
        self._repo.upsert(record.to_dict())

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str) -> bool:
        if name in self.data:
            del self.data[name]
            self._repo.delete(name)
            return True
        return False

    def save_record(self, record: Record):
        """Call after mutating an existing record."""
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

                if congratulation_date.weekday() == 5:   # Saturday → Monday
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Sunday → Monday
                    congratulation_date += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                })

        return upcoming
