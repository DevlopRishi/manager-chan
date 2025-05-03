# Main entry point for the Manager-chan Notes application.
# Handles argument parsing and initializes the TUI.
import argparse
import sys
import os

# Ensure the src directory is potentially findable if running script directly
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from .settings import AppSettings
    from .logic import NoteManager
    from .tui import ForgetfulNotesApp
    # from .constants import APP_DATA_DIR # If using AppDirs later
except ImportError as e:
     # Helpful error if run directly without installing package
     print(f"Import Error: {e}")
     print("Ensure you are running this as part of the installed package or have set up the PYTHONPATH correctly.")
     sys.exit(1)

def run_app():
    """Initializes and runs the main application."""
    parser = argparse.ArgumentParser(description="Manager-chan's Forgetful Notes App")
    parser.add_argument(
        "--dont-forget",
        action="store_true",
        help="Manager-chan tries EXTRA hard and disables all forgetfulness for this session."
    )
    # Add other arguments if needed (e.g., --config-dir)
    args = parser.parse_args()

    # Initialize components
    app_settings = AppSettings()
    note_manager = NoteManager(settings=app_settings, dont_forget_flag=args.dont_forget)
    tui_app = ForgetfulNotesApp(settings=app_settings, note_manager=note_manager)

    # Run the TUI application
    tui_app.run()

if __name__ == "__main__":
    # This allows running the script directly for testing (python src/manager_chan_notes/main.py)
    # But the intended way is via the installed 'manager-chan' command
    run_app()
