# Manager-chan's Forgetful Notes App 🧠📝

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)

**Your slightly chaotic but surprisingly capable TUI (Text User Interface) notes and task manager, guided by the ever-forgetful Manager-chan!**

Welcome to the official repository for Manager-chan Notes! She tries her *absolute best* to keep track of your notes, tasks, and ideas directly in your terminal. She offers features found in powerful note-taking apps, but with a unique twist: she's prone to forgetting things over time and occasionally misspelling words. Don't worry, it's (mostly) configurable!

**(Maby I'll upload images here)**
```

       /\_/\
      ( o.o )   Hi! I'm Manager-chan!
      > ^ <    Let's check the Repo...
     /  |  \
    /   |   \
   (____|____)
```

## ✨ Features

*   **Full TUI Interface:** Clean, keyboard-driven terminal UI powered by `prompt_toolkit`.
*   **Rich Note Formatting:** Write notes using **Markdown**! Rendered beautifully in the details pane with `rich`.
*   **Comprehensive Metadata:** Organize notes with:
    *   ✅ Status (Todo, In Progress, Done, Archived)
    *   ❗ Priority (A, B, C)
    *   🏷️ Tags (Multiple, comma-separated)
    *   📅 Due Dates (YYYY-MM-DD)
    *   🕒 Creation & Modification Timestamps
*   **Powerful Management:**
    *   🔄 **Sorting:** Sort by priority, due date, status, creation/modification time, or text.
    *   🔎 **Filtering:** Filter by status, priority, tag, or archived status.
    *   📝 **Search:** Quickly search through note titles and content.
*   **Manager-chan Persona:** Cute ASCII art and contextual status messages provide personality (can be disabled).
*   **Configurable Forgetfulness:** Manager-chan might "forget" older items based on configurable probability and time windows.
*   **Configurable Misspelling:** She might also occasionally misspell words during display (can be configured to save permanently, default is display-only).
*   **Settings Panel:** Tweak forgetfulness, misspelling, and other options via an in-app settings panel (`Ctrl+S`).
*   **Persistence:** Notes and settings are saved locally in JSON files (`manager_chan_notes.json`, `manager_chan_settings.json`) in the current directory.

## 🤔 The Forgetful Mechanic (It's a Feature!)

Manager-chan's defining characteristic is her unreliable memory. This isn't just a bug, it's a core (and configurable) part of the experience:

1.  **Timed Forgetting:** Notes don't vanish immediately. Forgetting only *starts* after a configurable delay (default: 7 days).
2.  **Probability Window:** The *chance* of an item being forgotten increases gradually over a configurable time window following the initial delay (default: 14 days).
3.  **Configurable:** You can adjust the delay, the window, the base probability, or disable forgetting entirely via the Settings Panel (`Ctrl+S`).
4.  **`--dont-forget` Flag:** Use this command-line argument for sessions where you absolutely cannot risk losing information.
5.  **Misspelling:** A separate, configurable chance for Manager-chan to make minor typos when displaying text. By default, these are *not* saved permanently, but this can be changed in settings. Much useful for memory management.

This mechanic adds a unique, slightly unpredictable element. Can you get things done before Manager-chan forgets them?

## 🚀 Installation

You need Python 3.7 or later and `pip`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DevlopRishi/manager-chan.git
    cd manager-chan
    ```
2.  **Install the package using pip:**
    This command builds the package and installs it, along with its dependencies (`prompt_toolkit`, `rich`), and makes the `manager-chan` command available.
    ```bash
    pip install .
    ```
    *Alternatively, for development, you can install in editable mode:*
    ```bash
    pip install -e .
    ```

## 💻 Usage

Once installed, run the application from anywhere in your terminal using the command:

```bash
manager-chan
```

To run without any forgetfulness or misspelling for the current session:

```bash
manager-chan --dont-forget
```

Your notes (`manager_chan_notes.json`) and settings (`manager_chan_settings.json`) will be saved in the directory where you run the command.

## ⌨️ Keybindings

| Key         | Action                           | Description                                      |
| :---------- | :------------------------------- | :----------------------------------------------- |
| `Up`/`Down` | Navigate List                    | Select the previous/next note.                   |
| `PgUp`/`PgDn`| Page Up/Down List              | Scroll the list view by pages.                   |
| `Home`/`End`| Go to Start/End                  | Jump to the first/last note in the list.         |
| `Enter`     | Toggle Details Pane              | Show/hide the detailed view for the selected note. |
| `Tab`       | Toggle Details Pane              | Alternative for showing/hiding details.          |
| `a`         | Add Note                         | Open the dialog to create a new note.            |
| `e`         | Edit Note                        | Open the dialog to edit the selected note.       |
| `d`         | Delete Note                      | Show confirmation dialog to delete selected note. |
| `space`     | Cycle Status                     | Change status: Todo > In Progress > Done > Archived |
| `p`         | Cycle Priority                   | Change priority: None > A > B > C > None         |
| `s`         | Sort Menu                        | Open dialog to choose sorting criteria.          |
| `f`         | Filter Menu / Clear Filter       | Open filter dialog, or clear active filters.     |
| `/`         | Search / Clear Search            | Open search dialog, or clear active search.      |
| `h` / `?`   | Help                             | Show the help dialog with keybindings.           |
| `Ctrl+S`    | Settings                         | Open the application settings panel.             |
| `Ctrl+C`    | Quit                             | Exit the application (attempts to save).         |
| `Ctrl+Q`    | Quit                             | Exit the application (attempts to save).         |

## ⚙️ Configuration

*   Press `Ctrl+S` within the app to access the Settings panel.
*   You can configure:
    *   Forgetfulness parameters (enable, delay, window, probability)
    *   Misspelling parameters (enable, probability, save permanently)
    *   Whether to display Manager-chan's ASCII art
*   Settings are saved to `manager_chan_settings.json`.

## 📁 File Structure (Simplified)

*   `src/manager_chan_notes/`: Contains the core Python package source code (split into modules like `tui.py`, `logic.py`, etc.).
*   `pyproject.toml`: Defines the package, dependencies, and build process.
*   `README.md`: This file.
*   `LICENSE`: The MIT License file.

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature suggestion, or want to improve the app:

1.  Check for existing issues: [https://github.com/DevlopRishi/manager-chan/issues](https://github.com/DevlopRishi/manager-chan/issues)
2.  If your issue isn't listed, open a new one.
3.  If you'd like to contribute code:
    *   Fork the repository ([https://github.com/DevlopRishi/manager-chan/fork](https://github.com/DevlopRishi/manager-chan/fork)).
    *   Create a new branch for your feature (`git checkout -b feature/your-feature-name`).
    *   Make your changes. Consider installing in editable mode (`pip install -e .`) for testing.
    *   Commit your changes (`git commit -am 'Add some feature'`).
    *   Push to the branch (`git push origin feature/your-feature-name`).
    *   Open a Pull Request back to the `main` branch of `DevlopRishi/manager-chan`.

Please try to maintain the existing coding style and add comments where necessary. 🙏

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

*   [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for the awesome TUI library.
*   [rich](https://github.com/Textualize/rich) for beautiful terminal rendering, especially Markdown.
```