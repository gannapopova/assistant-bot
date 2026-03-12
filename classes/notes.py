import uuid
from datetime import datetime


def _now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M")


class Note:
    def __init__(
        self,
        text: str,
        tags: list[str] = None,
        note_id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.id = note_id or str(uuid.uuid4())
        self.text = text
        self.tags = tags or []
        self.created_at = created_at or _now()
        self.updated_at = updated_at or self.created_at

    def add_tag(self, tag: str):
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        self.tags = [t for t in self.tags if t != tag.strip().lower()]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            text=data["text"],
            tags=data.get("tags", []),
            note_id=data["id"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __str__(self):
        tags_str = f"  [{', '.join(self.tags)}]" if self.tags else ""
        return f"{self.created_at}\n{self.text}{tags_str}"
