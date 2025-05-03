# Defines the Text User Interface (TUI) for the application using prompt_toolkit.
import datetime
import textwrap
from typing import List, Dict, Optional, Tuple, Any
from io import StringIO

# --- TUI and Rich Text Libs ---
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, ConditionalContainer, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import ANSI, HTML, merge_formatted_text, to_formatted_text
from prompt_toolkit.widgets import Box, Button, Dialog, Label, TextArea, Checkbox, RadioList
from prompt_toolkit.styles import Style

# Using rich for Markdown rendering
from rich.console import Console as RichConsole
from rich.markdown import Markdown as RichMarkdown
from rich.theme import Theme

# --- Internal Imports ---
from .data_models import NoteItem
from .settings import AppSettings
from .logic import NoteManager, misspell_text # Import logic components
from .constants import ( # Import constants and messages
    STATUS_OPTIONS, PRIORITY_OPTIONS, DEFAULT_MISSPELL_PROBABILITY,
    MANAGER_CHAN_MESSAGES, HELP_TEXT, DEFAULT_SORT
)
from .art import MANAGER_CHAN_ART # Import art


class ForgetfulNotesApp:
    def __init__(self, settings: AppSettings, note_manager: NoteManager):
        self.settings = settings
        self.note_manager = note_manager
        self.app: Optional[Application] = None
        self.selected_index = 0
        self.display_notes: List[NoteItem] = []
        self.current_sort = self.settings.get("default_sort", DEFAULT_SORT)
        self.current_filters: Dict = {"archived": False} # Default: hide archived
        self.current_search: Optional[str] = None
        self.show_details_pane = False
        self.active_dialog = None # To manage pop-up dialogs
        self.status_message = MANAGER_CHAN_MESSAGES["welcome"] # TUI manages its own status
        self.manager_art = MANAGER_CHAN_ART["idle"] # TUI manages its own art state

        # Rich console for Markdown rendering to string buffer
        # Define a simple theme for rich markdown
        self.rich_theme = Theme({
                 "markdown.h1": "bold underline", "markdown.h2": "bold",
                 "markdown.code": "dim cyan", "markdown.link": "underline blue",
                 "markdown.bold": "bold", "markdown.italic": "italic"
        })
        self.rich_console = RichConsole(file=StringIO(), width=80, theme=self.rich_theme) # Adjust width as needed

        # --- Key Bindings ---
        self.kb = KeyBindings()
        self._setup_keybindings()

        # --- UI Components ---
        self.list_view_control = FormattedTextControl(focusable=True, key_bindings=self.kb)
        self.details_view_control = FormattedTextControl(focusable=True, key_bindings=self.kb) # Read-only details
        self.status_bar_control = FormattedTextControl()
        self.manager_view_control = FormattedTextControl()

        # --- Layout ---
        self.list_window = Window(content=self.list_view_control, style="class:list-view", wrap_lines=False) # No wrap in list
        self.details_window = Window(content=self.details_view_control, style="class:details-view", wrap_lines=True) # Wrap details
        self.manager_window = Window(content=self.manager_view_control, height=6, style="class:manager-view", wrap_lines=False)

        self.body_container = VSplit([
            self.list_window,
            ConditionalContainer(
                 Window(width=1, char='│', style='class:separator'), # Vertical separator
                 filter=lambda: self.show_details_pane
            ),
            ConditionalContainer(
                self.details_window,
                filter=lambda: self.show_details_pane
            )
        ])

        self.root_container = HSplit([
            ConditionalContainer(self.manager_window, filter=lambda: self.settings.get("show_manager_chan", True)),
            Window(height=1, char='─', style='class:separator'), # Horizontal separator
            self.body_container,
            Window(height=1, char='─', style='class:separator'),
            Window(content=self.status_bar_control, height=1, style="class:status-bar"),
        ])

        # FloatContainer for dialogs
        self.float_container = FloatContainer(
             content=self.root_container,
             floats=[] # Dialogs will be added here
        )

        self.layout = Layout(self.float_container)

        # --- Styling (Copied from previous, adjust as needed) ---
        self.style = Style.from_dict({
            'list-view': 'bg:#202020 #d0d0d0',
            # 'list-view focused': 'bg:#303030 #ffffff', # Use focused pseudo-class if needed later
            'list-view.selected': 'bg:#005f87 #ffffff bold',
            'details-view': 'bg:#252525 #c0c0c0',
            'status-bar': 'bg:#005f5f #ffffff bold',
            'manager-view': 'bg:#1c1c1c #d0d0d0',
            'separator': 'fg:#444444',
            'dialog':             'bg:#404040',
            'dialog frame.label': 'fg:#ffffff bg:#005f87 bold', # Note: use frame.label
            'dialog.body':        'bg:#505050 #ffffff',
            'dialog shadow':      'bg:#202020',
            'button': 'bg:#005f87 #ffffff', # Non-focused button
            'button.focused': 'bg:#0087af #ffffff bold underline', # Focused button
            'button.disabled': 'fg:#888888 bg:#404040', # Example disabled style
            'text-area':          'bg:#606060 #f0f0f0',
            'text-area.focused':  'bg:#707070 #ffffff',
            'checkbox':           '#ffffff',
            'checkbox.checked':   'bold #00ff00',
            'radio':              '#ffffff',
            'radio.selected':     'bold #00ff00',
            # Styles for list items
            'status.Todo': 'fg:#d0d0d0',
            'status.InProgress': 'fg:#ffff00', # Fixed typo
            'status.Done': 'fg:#00ff00',
            'status.Archived': 'fg:#808080',
            'priority.A': 'fg:#ff4040 bold',
            'priority.B': 'fg:#ff8000',
            'priority.C': 'fg:#a0a000',
            'tags': 'fg:#8080ff',
            'misspelled': 'fg:#ff8080 underline', # Highlight misspelled words
            'due.overdue': 'fg:#ff0000 bg:#400000',
            'due.today': 'fg:#ffff00 bg:#404000 bold',
            'due.future': 'fg:#d0d0d0', # Style for future due dates
        })

        # Initial load and UI update
        load_msg, load_art = self.note_manager._load_notes() # Load notes via manager
        self.status_message = load_msg
        self.manager_art = load_art
        self._update_display_list() # Populate display list
        self._redraw_ui()           # Initial draw


    def _setup_keybindings(self):
        kb = self.kb

        @kb.add('c-c', eager=True)
        @kb.add('c-q', eager=True)
        def _quit(event):
            """Quit the application."""
            # Attempt save before exiting
            save_msg, _ = self.note_manager.save_notes()
            event.app.exit(result=f"Quit by user. ({save_msg})")

        @kb.add('up')
        def _up(event):
            if self.display_notes:
                self.selected_index = (self.selected_index - 1 + len(self.display_notes)) % len(self.display_notes)
                self._redraw_ui(list_only=True) # Efficient redraw

        @kb.add('down')
        def _down(event):
            if self.display_notes:
                self.selected_index = (self.selected_index + 1) % len(self.display_notes)
                self._redraw_ui(list_only=True) # Efficient redraw

        @kb.add('pageup')
        def _pageup(event):
            if self.display_notes:
                 # Adjust page size as needed (e.g., based on window height)
                 page_size = 10
                 self.selected_index = max(0, self.selected_index - page_size)
                 self._redraw_ui(list_only=True)

        @kb.add('pagedown')
        def _pagedown(event):
             if self.display_notes:
                 page_size = 10
                 self.selected_index = min(len(self.display_notes) - 1, self.selected_index + page_size)
                 self._redraw_ui(list_only=True)

        @kb.add('home')
        def _home(event):
            if self.display_notes:
                self.selected_index = 0
                self._redraw_ui(list_only=True)

        @kb.add('end')
        def _end(event):
             if self.display_notes:
                 self.selected_index = len(self.display_notes) - 1
                 self._redraw_ui(list_only=True)


        @kb.add('enter')
        def _enter(event):
             # Toggle details view or perform default action? Let's toggle details.
             self.show_details_pane = not self.show_details_pane
             self._redraw_ui() # Redraw needed components

        @kb.add('tab') # Might be used by toolkit, check focus behavior
        def _tab(event):
             # If details pane is visible, maybe focus it? Needs more focus management.
             # For now, just toggle like Enter.
             self.show_details_pane = not self.show_details_pane
             self._redraw_ui()

        @kb.add('a') # Add Note
        def _add(event):
             self._show_edit_dialog(None) # Pass None for adding new

        @kb.add('e') # Edit Note
        def _edit(event):
            selected_note = self._get_selected_note()
            if selected_note:
                self._show_edit_dialog(selected_note)

        @kb.add('d') # Delete Note
        def _delete(event):
             selected_note = self._get_selected_note()
             if selected_note:
                  title = MANAGER_CHAN_MESSAGES["confirm_delete_title"]
                  text = MANAGER_CHAN_MESSAGES["confirm_delete_text"].format(text=selected_note.text[:30])
                  self._show_confirm_dialog(
                      title=title,
                      text=text,
                      confirm_handler=lambda: self._confirm_delete(selected_note.id)
                  )

        @kb.add('space') # Toggle Status (Cycle)
        def _toggle_status(event):
            selected_note = self._get_selected_note()
            if selected_note:
                try:
                    current_status_index = STATUS_OPTIONS.index(selected_note.status)
                    next_status_index = (current_status_index + 1) % len(STATUS_OPTIONS)
                    selected_note.status = STATUS_OPTIONS[next_status_index]

                    if self.note_manager.update_note(selected_note):
                        save_msg, save_art = self.note_manager.save_notes()
                        self.manager_art = save_art
                        self._update_display_list() # Re-filter/sort might be needed
                        self._redraw_ui(status_msg=MANAGER_CHAN_MESSAGES["status_update"].format(status=selected_note.status))
                    else:
                         self._redraw_ui(status_msg="Error updating status (note not found?)")

                except ValueError:
                    # Handle case where status is somehow invalid
                    selected_note.status = STATUS_OPTIONS[0] # Reset to default
                    self.note_manager.update_note(selected_note)
                    self.note_manager.save_notes()
                    self._update_display_list()
                    self._redraw_ui(status_msg="Invalid status reset to Todo.")


        @kb.add('p') # Change Priority (Cycle)
        def _change_priority(event):
             selected_note = self._get_selected_note()
             if selected_note:
                  current_prio = selected_note.priority
                  options = [None] + PRIORITY_OPTIONS # None -> A -> B -> C -> None
                  try:
                      current_index = options.index(current_prio)
                  except ValueError:
                      current_index = 0 # Default to index of None if invalid
                  next_index = (current_index + 1) % len(options)
                  selected_note.priority = options[next_index]

                  if self.note_manager.update_note(selected_note):
                      save_msg, save_art = self.note_manager.save_notes()
                      self.manager_art = save_art
                      self._update_display_list() # Re-sort needed
                      self._redraw_ui(status_msg=MANAGER_CHAN_MESSAGES["priority_update"].format(priority=selected_note.priority or 'None'))
                  else:
                      self._redraw_ui(status_msg="Error updating priority (note not found?)")

        @kb.add('s') # Sort Menu
        def _sort_menu(event):
            self._show_sort_dialog()

        @kb.add('f') # Filter Menu / Clear Filter
        def _filter_menu(event):
             # Check if filters *other than default archived=False* are active, or if search is active
             non_default_filters = {k: v for k, v in self.current_filters.items() if k != 'archived' or v != False}
             if non_default_filters or self.current_search:
                 self.current_filters = {"archived": False} # Reset to default
                 self.current_search = None
                 self._update_display_list()
                 self._redraw_ui(status_msg=MANAGER_CHAN_MESSAGES["filters_cleared"])
             else:
                 self._show_filter_dialog()

        @kb.add('/') # Search
        def _search(event):
            if self.current_search: # Clear search if already active
                self.current_search = None
                self._update_display_list()
                self._redraw_ui(status_msg=MANAGER_CHAN_MESSAGES["search_cleared"])
            else:
                self._show_search_dialog()

        @kb.add('h') # Help
        @kb.add('?')
        def _help(event):
            self._show_help_dialog()

        @kb.add('ctrl-s') # Settings
        def _settings(event):
            self._show_settings_dialog()


    def _get_selected_note(self) -> Optional[NoteItem]:
        """Safely gets the currently selected note item."""
        if self.display_notes and 0 <= self.selected_index < len(self.display_notes):
            return self.display_notes[self.selected_index]
        return None

    def _apply_misspelling(self, text: str) -> Tuple[Any, bool]:
        """Applies misspelling based on settings and returns FormattedText, bool."""
        if not self.settings.get("misspell_enabled", True):
            return to_formatted_text(text), False

        probability = self.settings.get("misspell_probability", DEFAULT_MISSPELL_PROBABILITY)
        misspelled_text, was_misspelled = misspell_text(text, probability)

        if was_misspelled:
            # Simple approach: mark the whole string with a style if any part was misspelled.
            return to_formatted_text(HTML(f'<style class="misspelled">{misspelled_text}</style>')), True
        else:
            return to_formatted_text(misspelled_text), False

    def _format_note_for_list(self, note: NoteItem, is_selected: bool) -> Any:
        """Formats a single note line for the list view."""
        status_style = f"class:status.{note.status.replace(' ', '')}"
        prio_style = f"class:priority.{note.priority}" if note.priority else ""
        tag_style = "class:tags"

        # Indicators
        status_indicator = f"[{note.status[0] if note.status else '?'}]" # Handle potential empty status?
        prio_indicator = f"({note.priority})" if note.priority else "   "
        tags_str = f" {{{','.join(note.tags)}}}" if note.tags else ""

        # Apply misspelling to text (display only unless configured otherwise)
        display_text, was_misspelled_text = self._apply_misspelling(note.text)
        if was_misspelled_text and not is_selected:
            # Add visual cue (e.g., '?') if misspelled and not selected
            display_text = merge_formatted_text([to_formatted_text(HTML('<style fg="yellow">?</style>')), to_formatted_text(" "), display_text])

        # Due date indicator with styling
        due_indicator = ""
        due_style = ""
        if note.due_date:
            today = datetime.date.today()
            if note.due_date < today:
                due_indicator = f" !{note.due_date.strftime('%b%d')}!"
                due_style = "class:due.overdue"
            elif note.due_date == today:
                due_indicator = f" @{note.due_date.strftime('%b%d')}@"
                due_style = "class:due.today"
            else:
                 due_indicator = f" {note.due_date.strftime('%b%d')}"
                 due_style = "class:due.future" # Style for future dates


        # Combine parts with styles using merge_formatted_text for robustness
        formatted_line = merge_formatted_text([
            to_formatted_text(HTML(f'<{status_style}>{status_indicator}</{status_style}>')),
            to_formatted_text(f" "),
            to_formatted_text(HTML(f'<{prio_style}>{prio_indicator}</{prio_style}>') if prio_style else prio_indicator),
            to_formatted_text(f" "),
            display_text, # Already formatted text
            to_formatted_text(tags_str, style=tag_style),
            to_formatted_text(due_indicator, style=due_style)
        ])

        # Apply selection style wrapper if selected
        if is_selected:
             return to_formatted_text(formatted_line, style="class:list-view.selected")
        else:
            return formatted_line

    # --- UI Update Functions ---
    def _redraw_ui(self, status_msg: Optional[str] = None, list_only=False):
         """Central function to update UI components."""
         if status_msg:
              self.status_message = status_msg # Allow overriding status

         self._update_list_view()
         if not list_only:
              self._update_details_view()
              self._update_manager_view() # Update art only if needed

         # Status bar always updates
         self._update_status_bar()

         # Crucial: Invalidate the layout to trigger redraw in prompt_toolkit
         if self.app:
             self.app.invalidate()


    def _update_list_view(self):
        """Updates the content of the list view pane."""
        formatted_lines = []
        for i, note in enumerate(self.display_notes):
            is_selected = (i == self.selected_index)
            formatted_lines.append(self._format_note_for_list(note, is_selected))
            # Add line break - prompt toolkit handles lines, no need for explicit ""
            # formatted_lines.append(to_formatted_text(""))

        if not self.display_notes:
            if self.current_search:
                 empty_msg = f"No results for '{self.current_search}'"
            elif self.current_filters != {"archived": False}:
                 empty_msg = "No notes match filters."
            else:
                 empty_msg = MANAGER_CHAN_MESSAGES["empty"]
            formatted_lines.append(to_formatted_text(empty_msg, style="fg:gray"))

        self.list_view_control.text = merge_formatted_text(formatted_lines)


    def _update_details_view(self):
        """Updates the content of the details view pane."""
        if not self.show_details_pane:
            self.details_view_control.text = "" # Clear if hidden
            return

        selected_note = self._get_selected_note()
        if not selected_note:
            self.details_view_control.text = to_formatted_text("No note selected.", style="fg:gray")
            return

        # Render Markdown notes using Rich
        md_content = selected_note.notes
        # Apply misspelling *before* rendering Markdown if setting enabled
        rendered_notes_ansi = ""
        if md_content: # Only render if notes exist
             if self.settings.get("misspell_enabled", True):
                 md_content, _ = misspell_