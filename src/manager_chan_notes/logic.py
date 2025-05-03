# Handles the core application logic: managing notes data,
implementing forgetfulness and misspelling mechanics.
import json
import random
import os
import time
import datetime
import uuid
from typing import List, Dict, Optional, Tuple, Any

from .data_models import NoteItem
from .settings import AppSettings
from .constants import (
    NOTES_FILE_PATH, CURRENT_DATA_VERSION, DEFAULT_FORGET_DELAY_DAYS,
    DEFAULT_FORGET_WINDOW_DAYS, DEFAULT_FORGET_PROBABILITY, STATUS_OPTIONS,
    PRIORITY_OPTIONS, MANAGER_CHAN_MESSAGES
)
from .art import MANAGER_CHAN_ART # Import art for status updates


# --- Misspelling Function ---
def misspell_text(text: str, probability: float) -> Tuple[str, bool]:
    """Sometimes introduces a small typo. Returns (new_text, was_misspelled)."""
    if not text or not isinstance(text, str) or random.random() > probability:
        return text, False

    words = text.split()
    if not words: return text, False

    eligible_words = [(i, w) for i, w in enumerate(words) if len(w) > 3]
    if not eligible_words: return text, False

    word_index_in_list, target_word = random.choice(eligible_words)
    # Find original index robustly in case of duplicate words
    original_word_indices = [i for i, w in enumerate(words) if w == target_word]
    if not original_word_indices: return text, False # Should not happen
    original_word_index = random.choice(original_word_indices)

    mutated_word = list(target_word)
    if not mutated_word: return text, False # Empty word somehow

    pos = random.randint(0, len(target_word) - 1)
    action = random.choice(['swap', 'replace', 'delete', 'duplicate'])

    try:
        if action == 'swap' and pos < len(target_word) - 1:
            mutated_word[pos], mutated_word[pos+1] = mutated_word[pos+1], mutated_word[pos]
        elif action == 'replace':
            # Replace with a nearby character (very simplified)
            replacement_chars = "abcdefghijklmnopqrstuvwxyz"
            if mutated_word[pos].isupper():
                replacement_chars = replacement_chars.upper()
            mutated_word[pos] = random.choice(replacement_chars)
        elif action == 'delete' and len(mutated_word) > 1:
            del mutated_word[pos]
        elif action == 'duplicate' and len(mutated_word) < 30: # Prevent runaway duplication
             mutated_word.insert(pos, mutated_word[pos])
        else: # Fallback if action is invalid for position/length
             return text, False
    except IndexError:
        return text, False # Safety

    words[original_word_index] = "".join(mutated_word)
    return " ".join(words), True


# --- Forgetfulness Calculation ---
def calculate_forget_chance(item: NoteItem, settings: AppSettings) -> float:
    """Calculates the probability of forgetting an item based on age and settings."""
    if not settings.get("forget_enabled", True): # Default to True if somehow missing
        return 0.0

    now = datetime.datetime.now()
    # Use modified_at as the basis for forgetting? Or created_at? Let's use modified_at.
    last_touched_at = item.modified_at or item.created_at
    if last_touched_at is None:
        return 0.0 # Cannot calculate age

    # Ensure 'now' is offset-naive if 'last_touched_at' is, or vice-versa
    # Assuming both are naive for simplicity based on NoteItem defaults
    if now.tzinfo != last_touched_at.tzinfo:
         # This indicates a potential timezone issue, log or handle appropriately
         # For now, let's proceed assuming naive comparison is intended
         pass


    age = now - last_touched_at
    delay_days = settings.get("forget_delay_days", DEFAULT_FORGET_DELAY_DAYS)
    window_days = settings.get("forget_window_days", DEFAULT_FORGET_WINDOW_DAYS)
    base_prob = settings.get("forget_base_probability", DEFAULT_FORGET_PROBABILITY)

    # Validate settings values
    delay_days = max(0, int(delay_days))
    window_days = max(0, int(window_days))
    base_prob = max(0.0, min(1.0, float(base_prob)))

    if age.days < delay_days or window_days <= 0:
        return 0.0 # Not old enough or no forget window

    # Calculate how far into the forget window the item is (as a fraction)
    days_into_window = max(0.0, float(age.days - delay_days))
    forget_progress = min(1.0, days_into_window / float(window_days))

    # Linear increase in probability over the window
    current_prob = base_prob * forget_progress

    return min(current_prob, 1.0) # Cap probability at 1.0


# --- Note Management Class ---
class NoteManager:
    def __init__(self, settings: AppSettings, dont_forget_flag: bool = False):
        self.settings = settings
        self.notes: List[NoteItem] = []
        # Status message and art are better handled by the TUI class
        # self.status_message = ""
        # self.manager_art = MANAGER_CHAN_ART["idle"]
        self.dont_forget = dont_forget_flag or not self.settings.get("forget_enabled")
        self._load_notes() # Load notes on initialization

    def _load_notes(self) -> Tuple[str, Any]:
        """Loads notes, applies forgetfulness, returns status msg & art."""
        status_message = MANAGER_CHAN_MESSAGES["loading"]
        manager_art = MANAGER_CHAN_ART["thinking"]
        remembered_notes: List[NoteItem] = []
        forgotten_count = 0
        raw_notes_data = []

        # Chance to forget the *entire file* path (simulated by trying to rename)
        # Reduce chance slightly compared to previous example
        if not self.dont_forget and random.random() < 0.005 and os.path.exists(NOTES_FILE_PATH):
            try:
                ts = int(time.time())
                os.rename(NOTES_FILE_PATH, f"{NOTES_FILE_PATH}.forgotten_{ts}")
                status_message = MANAGER_CHAN_MESSAGES["forgot_file"].format(filename=NOTES_FILE_PATH)
                manager_art = MANAGER_CHAN_ART["sad"]
                self.notes = []
                return status_message, manager_art # Start fresh
            except OSError as e:
                 print(f"Warning: Failed to rename notes file for 'forgetting': {e}")
                 pass # Ignore if rename fails, proceed as normal

        try:
            with open(NOTES_FILE_PATH, 'r') as f:
                data = json.load(f)

            # Basic version/format check
            if isinstance(data, dict) and "version" in data and "notes" in data:
                if data["version"] > CURRENT_DATA_VERSION:
                     print(f"Warning: Notes file version ({data['version']}) is newer than app ({CURRENT_DATA_VERSION}). Loading might be unstable.")
                # We assume forward compatibility for now, or add migration logic
                raw_notes_data = data.get("notes", [])
                if not isinstance(raw_notes_data, list):
                     print(f"Warning: 'notes' key in file is not a list. Starting fresh.")
                     raw_notes_data = []

            elif isinstance(data, list): # Support older format (just a list)
                 status_message = "Old note format detected. Loading..."
                 raw_notes_data = data
            else:
                raise ValueError("Unknown file format")

        except FileNotFoundError:
            status_message = f"No notes file found at '{NOTES_FILE_PATH}'. Starting fresh!"
            self.notes = []
            manager_art = MANAGER_CHAN_ART["idle"] # Reset art
            return status_message, manager_art
        except (json.JSONDecodeError, ValueError) as e:
            status_message = f"Notes file '{NOTES_FILE_PATH}' is corrupted or invalid ({e}). Starting fresh!"
            self.notes = []
            manager_art = MANAGER_CHAN_ART["sad"]
            return status_message, manager_art
        except Exception as e:
            status_message = f"Unexpected error loading notes: {e}. Starting fresh!"
            self.notes = []
            manager_art = MANAGER_CHAN_ART["sad"]
            return status_message, manager_art


        # Process loaded notes: Forgetfulness
        for item_dict in raw_notes_data:
            if not isinstance(item_dict, dict):
                 print(f"Warning: Found non-dictionary item in notes file, skipping: {item_dict}")
                 continue
            try:
                item = NoteItem.from_dict(item_dict)
                forget_chance = calculate_forget_chance(item, self.settings)

                if not self.dont_forget and random.random() < forget_chance:
                    forgotten_count += 1
                    # Maybe log forgotten items to a separate file for "recovery"?
                    # print(f"DEBUG: Forgetting '{item.text[:20]}...' (Chance: {forget_chance:.2f})")
                else:
                    remembered_notes.append(item)
            except Exception as e:
                # Log specific item error but continue loading others
                item_id = item_dict.get('id', item_dict.get('text', 'Unknown')[:20])
                print(f"Warning: Couldn't load note item '{item_id}': {e}. Skipping.")


        self.notes = remembered_notes
        if forgotten_count > 0:
            # TUI will display this status message
            status_message = f"Loaded {len(self.notes)} notes... but {forgotten_count} seemed to vanish! Gomen!"
            manager_art = MANAGER_CHAN_ART["sad"]
        else:
            status_message = f"Loaded {len(self.notes)} notes!"
            manager_art = MANAGER_CHAN_ART["idle"]

        return status_message, manager_art


    def save_notes(self) -> Tuple[str, Any]:
        """Saves notes, returns status msg & art."""
        status_message = MANAGER_CHAN_MESSAGES["saving"]
        manager_art = MANAGER_CHAN_ART["thinking"]
        data_to_save = {
            "version": CURRENT_DATA_VERSION,
            "notes": [item.to_dict() for item in self.notes]
        }
        try:
            # Ensure directory exists
            # os.makedirs(os.path.dirname(NOTES_FILE_PATH), exist_ok=True)
            with open(NOTES_FILE_PATH, 'w') as f:
                json.dump(data_to_save, f, indent=2) # Smaller indent saves space
            status_message = f"Saved {len(self.notes)} notes! Phew!"
            manager_art = MANAGER_CHAN_ART["happy"]
        except IOError as e:
            status_message = MANAGER_CHAN_MESSAGES["error"].format(error=e)
            manager_art = MANAGER_CHAN_ART["sad"]
        except Exception as e:
            status_message = MANAGER_CHAN_MESSAGES["error"].format(error=f"Unexpected save error: {e}")
            manager_art = MANAGER_CHAN_ART["sad"]

        return status_message, manager_art


    def add_note(self, note: NoteItem):
        """Adds a new note to the list."""
        note.modified_at = datetime.datetime.now().replace(microsecond=0) # Ensure modified time is set
        self.notes.append(note)
        # Save happens explicitly via TUI action now

    def update_note(self, updated_note: NoteItem):
        """Updates an existing note identified by ID."""
        for i, note in enumerate(self.notes):
            if note.id == updated_note.id:
                updated_note.modified_at = datetime.datetime.now().replace(microsecond=0)
                self.notes[i] = updated_note
                # Save happens explicitly via TUI action
                return True
        return False # Note not found

    def delete_note(self, note_id: str):
        """Deletes a note by its ID."""
        original_length = len(self.notes)
        self.notes = [note for note in self.notes if note.id != note_id]
        # Save happens explicitly via TUI action
        return len(self.notes) < original_length


    def find_note_by_id(self, note_id: str) -> Optional[NoteItem]:
        """Finds a single note by its unique ID."""
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def get_display_notes(self, sort_by: Optional[str] = None, filters: Optional[Dict] = None, search_query: Optional[str] = None) -> List[NoteItem]:
        """Applies filtering, searching, and sorting to return the list for display."""
        display_list = self.notes[:] # Start with a copy

        active_filters = filters or {}
        # Default filter: Hide archived unless explicitly requested
        if "archived" not in active_filters:
             active_filters["archived"] = False

        # 1. Filtering
        if not active_filters.get("archived", False): # Apply default archived filter
             display_list = [n for n in display_list if n.status != "Archived"]
        # Apply other filters if present
        if "status" in active_filters:
            display_list = [n for n in display_list if n.status == active_filters["status"]]
        if "priority" in active_filters:
            display_list = [n for n in display_list if n.priority == active_filters["priority"]]
        if "tag" in active_filters:
            tag_filter = active_filters["tag"].lower()
            display_list = [n for n in display_list if tag_filter in [t.lower() for t in n.tags]]
        # Add more filters here (e.g., due date ranges)

        # 2. Searching (if query provided)
        if search_query:
            query = search_query.lower()
            display_list = [
                n for n in display_list
                if query in n.text.lower() or query in n.notes.lower() or any(query in tag.lower() for tag in n.tags)
            ]

        # 3. Sorting
        sort_key = sort_by or self.settings.get("default_sort", DEFAULT_SORT)
        reverse_sort = False
        priority_map = {"A": 0, "B": 1, "C": 2, None: 99} # Lower number = higher prio

        def sort_func(item: NoteItem):
            # Define sort keys, handling None values appropriately (usually sort last)
            if sort_key == "priority":
                return priority_map.get(item.priority, 99)
            elif sort_key == "due_date":
                return item.due_date if item.due_date else datetime.date.max
            elif sort_key == "created_at":
                return item.created_at if item.created_at else datetime.datetime.min
            elif sort_key == "modified_at":
                nonlocal reverse_sort # Need to modify the outer scope variable
                reverse_sort = True # Show most recently modified first
                return item.modified_at if item.modified_at else datetime.datetime.min
            elif sort_key == "status":
                 status_order = {name: i for i, name in enumerate(STATUS_OPTIONS)}
                 return status_order.get(item.status, 99)
            elif sort_key == "text":
                 return item.text.lower()
            else: # Default fallback sort
                return item.created_at if item.created_at else datetime.datetime.min

        try:
            display_list.sort(key=sort_func, reverse=reverse_sort)
        except Exception as e:
            print(f"Error during sorting by '{sort_key}': {e}")
            # Potentially fall back to a default sort like creation date
            display_list.sort(key=lambda item: item.created_at if item.created_at else datetime.datetime.min)

        return display_list