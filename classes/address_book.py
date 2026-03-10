from collections import UserDict
from datetime import datetime, timedelta

from .fields import Name, Phone, Birthday


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

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

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones) or "no phones"
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"{self.name}: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self) -> list:
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

            if 0 <= delta_days <= 7:
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
