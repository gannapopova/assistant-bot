from datetime import datetime

import questionary
from colorama import Fore

_PAGE_SIZE = 10


def _pause():
    try:
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except KeyboardInterrupt:
        pass


def _print(msg: str):
    print(f"\n{msg}")


def _parse_dmy(s: str) -> datetime:
    if not s:
        return datetime.min
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return datetime.min


def _next_birthday(birthday_str: str) -> datetime:
    """Return the next upcoming occurrence of a birthday. No birthday → datetime.max (sorts last)."""
    if not birthday_str:
        return datetime.max
    try:
        bday = datetime.strptime(birthday_str, "%d.%m.%Y")
    except ValueError:
        return datetime.max
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    for year in (today.year, today.year + 1):
        try:
            candidate = bday.replace(year=year)
        except ValueError:
            candidate = bday.replace(year=year, day=28)  # Feb 29 in non-leap year
        if candidate >= today:
            return candidate
    return datetime.max


CONTACT_SORTS = [
    ("Name A→Z",               lambda r: r.name.value.lower(),                                              False),
    ("Name Z→A",               lambda r: r.name.value.lower(),                                              True),
    ("Birthday (soonest)",     lambda r: _next_birthday(str(r.birthday) if r.birthday else ""),             False),
    ("Created (newest first)", lambda r: _parse_dmy(r.created_at),                                          True),
    ("Created (oldest first)", lambda r: _parse_dmy(r.created_at),                                          False),
    ("Updated (newest first)", lambda r: _parse_dmy(r.updated_at),                                          True),
]

NOTE_SORTS = [
    ("Created (newest first)", lambda n: _parse_dmy(n.created_at), True),
    ("Created (oldest first)", lambda n: _parse_dmy(n.created_at), False),
    ("Updated (newest first)", lambda n: _parse_dmy(n.updated_at), True),
    ("Tags A→Z",               lambda n: n.tags[0].lower() if n.tags else "zzz", False),
]


def table_view(items: list, render_fn, sort_options: list, default_sort_idx: int = 0):
    """Generic paginated+sortable table view."""
    if not items:
        render_fn(items)
        _pause()
        return

    page = 0
    sort_idx = default_sort_idx
    sort_label, sort_key, sort_rev = sort_options[sort_idx]

    while True:
        sorted_items = sorted(items, key=sort_key, reverse=sort_rev)
        total = len(sorted_items)
        total_pages = (total + _PAGE_SIZE - 1) // _PAGE_SIZE
        page = min(page, total_pages - 1)
        page_items = sorted_items[page * _PAGE_SIZE:(page + 1) * _PAGE_SIZE]

        print()
        render_fn(page_items)
        print(f"\n  Page {page + 1}/{total_pages}  |  Sort: {sort_label}  |  Total: {total}")

        choices = ["Sort"]
        if page < total_pages - 1:
            choices.append("Next page")
        if page > 0:
            choices.append("Prev page")
        choices.append("Back")

        action = questionary.select("", choices=choices).ask()
        if action is None or action == "Back":
            break
        elif action == "Next page":
            page += 1
        elif action == "Prev page":
            page -= 1
        elif action == "Sort":
            sort_choices = [s[0] for s in sort_options] + ["Cancel"]
            picked = questionary.select("Sort by:", choices=sort_choices).ask()
            if picked and picked != "Cancel":
                sort_idx = next(i for i, s in enumerate(sort_options) if s[0] == picked)
                sort_label, sort_key, sort_rev = sort_options[sort_idx]
                page = 0
