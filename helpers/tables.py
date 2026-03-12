from rich.box import Box
from rich.console import Console
from rich.table import Table

# ROUNDED outer border, but dotted inner row dividers (visually lighter)
# Each line is exactly 4 chars: left, fill, divider, right
_ROUNDED_DOTTED_ROWS = Box(
    "╭─┬╮\n"  # top border
    "│ ││\n"  # head row
    "├─┼┤\n"  # head separator — solid
    "│ ││\n"  # mid row
    "├╌┼┤\n"  # row divider — dashed/lighter
    "├─┼┤\n"  # foot row separator
    "│ ││\n"  # foot row
    "╰─┴╯\n"  # bottom border
)

from classes import AddressBook, NoteBook

console = Console()


def _build_contacts_table(records) -> Table:
    table = Table(show_header=True, header_style="bold cyan", box=_ROUNDED_DOTTED_ROWS, show_lines=True, expand=True)
    table.add_column("#",        width=3)
    table.add_column("Name",     ratio=3)
    table.add_column("Surname",  ratio=3)
    table.add_column("Phones",   width=10)
    table.add_column("Birthday", width=10)
    table.add_column("Email",    ratio=4)
    table.add_column("Address",  ratio=5)

    for i, record in enumerate(records, 1):
        table.add_row(
            str(i),
            record.name.value,
            record.surname.value if record.surname else "",
            "\n".join(p.value for p in record.phones) or "—",
            str(record.birthday) if record.birthday else "",
            record.email.value if record.email else "",
            str(record.address) if record.address else "",
        )

    return table


def print_contacts_table(book: AddressBook):
    if not book.data:
        console.print("[yellow]No contacts saved.[/yellow]")
        return
    console.print(_build_contacts_table(book.data.values()))


def print_contacts_table_subset(records: list):
    if not records:
        console.print("[yellow]No contacts found.[/yellow]")
        return
    console.print(_build_contacts_table(records))


def print_notes_table(notes: list):
    if not notes:
        console.print("[yellow]No notes saved.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan", box=_ROUNDED_DOTTED_ROWS, show_lines=True, expand=True)
    table.add_column("#",    ratio=1)
    table.add_column("Text", ratio=8)
    table.add_column("Tags", ratio=3)

    for i, note in enumerate(notes, 1):
        table.add_row(
            str(i),
            note.text,
            ", ".join(note.tags) if note.tags else "",
        )

    console.print(table)
