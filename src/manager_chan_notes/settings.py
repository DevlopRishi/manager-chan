# Manages loading, saving, and accessing application settings.
import json
import os
from typing import Dict, Any
from .constants import (
    SETTINGS_FILE_PATH, CURRENT_DATA_VERSION, DEFAULT_FORGET_DELAY_DAYS,
    DEFAULT_FORGET_WINDOW_DAYS, DEFAULT_FORGET_PROBABILITY,
    DEFAULT_MISSPELL_PROBABILITY, DEFAULT_SORT
)

class AppSettings:
    def __init__(self):
        self.data: Dict[str, Any] = self._load()

    def _default_settings(self) -> Dict[str, Any]:
        return {
            "version": CURRENT_DATA_VERSION,
            "forget_enabled": True,
            "forget_delay_days": DEFAULT_FORGET_DELAY_DAYS,
            "forget_window_days": DEFAULT_FORGET_WINDOW_DAYS,
            "forget_base_probability": DEFAULT_FORGET_PROBABILITY,
            "misspell_enabled": True,
            "misspell_probability": DEFAULT_MISSPELL_PROBABILITY,
            "misspell_saves_permanently": False,
            "default_sort": DEFAULT_SORT,
            "show_manager_chan": True,
            # Add future settings here
        }

    def _load(self) -> Dict[str, Any]:
        defaults = self._default_settings()
        loaded_data = {}
        try:
            with open(SETTINGS_FILE_PATH, 'r') as f:
                loaded_data = json.load(f)
            if not isinstance(loaded_data, dict):
                 raise ValueError("Settings file format is not a dictionary.")
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Manager-chan: Settings file ({SETTINGS_FILE_PATH}) issue ({e}). Using defaults.")
            return defaults
        except Exception as e:
            print(f"Manager-chan: Unexpected error loading settings: {e}. Using defaults.")
            return defaults


        # Merge loaded data with defaults, ensuring all keys exist and version check
        final_data = defaults.copy()
        final_data.update(loaded_data) # Loaded data overrides defaults

        if final_data.get("version") != CURRENT_DATA_VERSION:
             print(f"Manager-chan: Settings file version mismatch (found {final_data.get('version')}, expected {CURRENT_DATA_VERSION}). Migrating/using defaults.")
             # Add migration logic here if needed for future versions
             final_data["version"] = CURRENT_DATA_VERSION # Force update version
             # Re-apply defaults for potentially missing keys after version change
             temp_data = self._default_settings()
             temp_data.update(final_data) # Keep user values where keys exist
             final_data = temp_data

        return final_data

    def save(self):
        try:
            # Ensure directory exists (important if using AppDirs later)
            # os.makedirs(os.path.dirname(SETTINGS_FILE_PATH), exist_ok=True)
            with open(SETTINGS_FILE_PATH, 'w') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
             # Need a way to report this in the TUI later
            print(f"Manager-chan: Waaah! Couldn't save settings! {e}")
        except Exception as e:
            print(f"Manager-chan PANIC! Unexpected error saving settings: {e}")


    def get(self, key: str, default: Any = None) -> Any:
        # Provide default from defaults if key missing entirely
        return self.data.get(key, self._default_settings().get(key, default))

    def set(self, key: str, value: Any):
        self.data[key] = value
        # Maybe add validation here later
        self.save() # Auto-save on change