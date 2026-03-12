# Assistant Bot

Personal assistant CLI for managing contacts and notes.

## Installation

```bash
pip install .
```

If pip doesen't work use 

```bash
pip3 install .
```

After installation the `assistant-bot` command is available globally.

## Usage

```bash
assistant-bot
```

Navigates an interactive menu. Use arrow keys to move, Enter to select.

---

## Contacts

| Action | Description |
|---|---|
| **Add contact** | Create a new contact: name, surname, phone (required, 10 digits), email, birthday, address |
| **Show all contacts** | Display all contacts in a paginated table with sorting |
| **Find contact** | Search by name, phone or email |
| **Edit contact** | Edit phone, surname, email, birthday or address of an existing contact |
| **Delete contact** | Delete a contact by selecting from the list |
| **Upcoming birthdays** | Show contacts with birthdays within N days (default: 7) |

### Contact fields

| Field | Format | Required |
|---|---|---|
| Name | Any text | Yes |
| Surname | Any text | No |
| Phone | 10 digits, e.g. `0501234567` | Yes (at least one) |
| Email | Standard email, e.g. `user@example.com` | No |
| Birthday | `DD.MM.YYYY`, e.g. `15.03.1990` | No |
| Address | Country, city, street, house, apartment, zip code | No |

### Contacts table sorting options

- Name A→Z / Z→A
- Birthday (soonest upcoming)
- Created (newest / oldest first)
- Updated (newest first)

---

## Notes

| Action | Description |
|---|---|
| **Add note** | Create a note with text and optional comma-separated tags |
| **Show all notes** | Display all notes in a paginated table with sorting |
| **Find note** | Full-text search across note text |
| **Edit note** | Edit text or tags of an existing note |
| **Delete note** | Delete a note by selecting from the list |
| **Find by tag** | Show all notes with a specific tag |
| **Show sorted by tags** | Show notes sorted alphabetically by first tag |

### Notes table sorting options

- Created (newest / oldest first)
- Updated (newest first)
- Tags A→Z

---

## Examples

```
# Launch the bot
assistant-bot

# Main Menu
> Contacts
> Notes
> Exit

# Add a contact
Contacts > Add contact
  Name: John
  Surname: Doe
  Phone: 0501234567
  Email: john@example.com
  Birthday: 15.03.1990

# Find contacts named "Anna"
Contacts > Find contact
  Search query: Anna

# Show upcoming birthdays in next 30 days
Contacts > Upcoming birthdays
  Days ahead: 30

# Add a note with tags
Notes > Add note
  Note text: Buy milk and bread
  Tags: shopping, groceries
```
