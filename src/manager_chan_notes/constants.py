# Defines constants and user-facing messages used throughout the application.

# File Paths
NOTES_FILE_NAME = "manager_chan_notes.json"
SETTINGS_FILE_NAME = "manager_chan_settings.json" # Using AppDirs might be better for real install

# Versioning
CURRENT_DATA_VERSION = 1

# Default Settings Values
DEFAULT_FORGET_DELAY_DAYS = 7
DEFAULT_FORGET_WINDOW_DAYS = 14
DEFAULT_FORGET_PROBABILITY = 0.15
DEFAULT_MISSPELL_PROBABILITY = 0.10
DEFAULT_SORT = "priority"

# Note Metadata Options
STATUS_OPTIONS = ["Todo", "In Progress", "Done", "Archived"]
PRIORITY_OPTIONS = ["A", "B", "C"] # A=High

# Manager-chan Messages (can be expanded)
MANAGER_CHAN_MESSAGES = {
    "welcome": "Let's get things organized... I hope!",
    "quit": "Saving (I think!)... Bye bye!",
    "forgot_item": "💭 Oopsie! I remember writing something about '{text}'... but it's gone now! Ehehe...",
    "forgot_file": "EHHHH?! Where did I put the notes file?! (`{filename}`) I can't find it! Starting over... Gomen!",
    "misspelled": "(Huh? Did I write that correctly...? 🤔)",
    "loading": "Let me see what I remember...",
    "saving": "Okay, writing this down... stay!",
    "error": "Waaah! Something went wrong: {error}",
    "empty": "List is empty! Or I forgot everything...",
    "filter_active": "Showing filtered notes. Press 'f' again to clear.",
    "search_active": "Showing search results for '{query}'. Press '/' again to clear.",
    "status_update": "Status changed to {status}",
    "priority_update": "Priority changed to {priority}",
    "note_added": "New note added!",
    "note_updated": "Note updated!",
    "note_deleted": "Note deleted!",
    "edit_cancelled": "Edit cancelled.",
    "delete_failed": "Failed to delete note (already gone?).",
    "settings_saved": "Settings saved!",
    "settings_error": "Settings error: {error}. Not saved.",
    "settings_cancelled": "Settings changes cancelled.",
    "sort_applied": "Sorted by {sort_key}",
    "filters_applied": "Filters applied: {filters}",
    "filters_cleared": "Filters and search cleared.",
    "search_applied": "Searching for: '{query}'",
    "search_cleared": "Search cleared.",
    "search_cancelled": "Search cancelled (empty).",
    "confirm_delete_title": "Confirm Delete",
    "confirm_delete_text": "Manager-chan: Really delete '{text}'?\nThis can't be undone (probably)!",
    "add_title": "Add New Note",
    "edit_title": "Edit Note ({id})",
    "text_empty_error": "Note text cannot be empty!",
    "due_date_error": "Invalid due date format (use YYYY-MM-DD). Ignoring.",
    "help_title": "Help",
    "sort_title": "Sort Notes By",
    "filter_title": "Filter Notes",
    "search_title": "Search Notes (Text & Notes)",
    "settings_title": "Application Settings",
}

HELP_TEXT = """Manager-chan's Forgetful Notes Help
-------------------------------------
Navigation:
  Up/Down: Select note
  Enter/Tab: Toggle details pane
  Ctrl+C / Ctrl+Q: Quit

Actions:
  a: Add new note
  e: Edit selected note
  d: Delete selected note
  space: Cycle status (Todo > In Prog > Done > Archived)
  p: Cycle priority (None > A > B > C)

View Control:
  s: Change Sort order
  f: Filter notes (or clear filters)
  /: Search notes (or clear search)

Other:
  h / ?: Show this help
  Ctrl+S: Open Settings panel
-------------------------------------
Manager-chan tries her best, but sometimes... she forgets! Ehehe...
"""
# Consider using AppDirs standard paths later for better system integration
APP_DATA_DIR = "." # Default to current dir for simplicity now
NOTES_FILE_PATH = f"{APP_DATA_DIR}/{NOTES_FILE_NAME}"
SETTINGS_FILE_PATH = f"{APP_DATA_DIR}/{SETTINGS_FILE_NAME}"