import re
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(f"Phone must be 10 digits: {value}")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Email(Field):
    _PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")

    def __init__(self, value):
        if not self._PATTERN.match(value):
            raise ValueError(f"Invalid email format: {value}")
        super().__init__(value)


class Address:
    def __init__(
        self,
        country: str = "",
        city: str = "",
        street: str = "",
        house: str = "",
        apartment: str = "",
        zip_code: str = "",
    ):
        if zip_code and not zip_code.isdigit():
            raise ValueError("Zip code must contain digits only")
        self.country = country
        self.city = city
        self.street = street
        self.house = house
        self.apartment = apartment
        self.zip_code = zip_code

    def to_dict(self) -> dict:
        return {
            "country": self.country,
            "city": self.city,
            "street": self.street,
            "house": self.house,
            "apartment": self.apartment,
            "zip_code": self.zip_code,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Address":
        return cls(
            country=data.get("country", ""),
            city=data.get("city", ""),
            street=data.get("street", ""),
            house=data.get("house", ""),
            apartment=data.get("apartment", ""),
            zip_code=data.get("zip_code", ""),
        )

    def __str__(self):
        parts = [
            self.country,
            self.city,
            self.street,
            self.house,
            self.apartment,
            self.zip_code,
        ]
        return ", ".join(p for p in parts if p)

    def __bool__(self):
        return bool(str(self))
