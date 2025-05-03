# Stores Manager-chan's ASCII art representations.
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text, merge_formatted_text

# Define styles used in the art for clarity
STYLE_MAGENTA = 'fg:magenta'
STYLE_CYAN = 'fg:cyan'
STYLE_YELLOW = 'fg:yellow'
STYLE_DIM = 'fg:#d0d0d0' # Dim gray/white
STYLE_DEFAULT = '' # Default terminal color

# Helper function to create multi-line art from lists of tuples
def create_art(lines: list[list[tuple[str, str]]]) -> FormattedText:
    formatted_lines = []
    for line_tuples in lines:
        formatted_lines.append(to_formatted_text(line_tuples))
        formatted_lines.append(to_formatted_text("\n")) # Add newline after each logical line
    # Remove the last extra newline
    if formatted_lines:
        formatted_lines.pop()
    return merge_formatted_text(formatted_lines)

# Define each art piece as a list of lines, where each line is a list of (style, text) tuples
ART_IDLE = create_art([
    [(STYLE_MAGENTA, '       /\\_/\\')],
    [(STYLE_CYAN,    '( o.o )'), (STYLE_DEFAULT, '   Hi! I\'m '), (STYLE_YELLOW, 'Manager-chan!')],
    [(STYLE_CYAN,    ' > ^ < '), (STYLE_DEFAULT, '    I\'ll *try* my best! Ehehe...')],
    [(STYLE_DIM,     '     /  |  \\')],
    [(STYLE_DIM,     '    /   |   \\')],
    [(STYLE_DIM,     '   (____|____)')]
])

ART_THINKING = create_art([
    [(STYLE_MAGENTA, '       /\\_/\\')],
    [(STYLE_CYAN,    '( o.o )'), (STYLE_DEFAULT, '   Hmmmm...')],
    [(STYLE_CYAN,    ' > ? < '), (STYLE_DEFAULT, '    Where did I put that...?')],
    [(STYLE_DIM,     '     /  |  \\')],
    [(STYLE_DIM,     '    /   |   \\')],
    [(STYLE_DIM,     '   (____|____)')]
])

ART_HAPPY = create_art([
    [(STYLE_MAGENTA, '       /\\_/\\')],
    [(STYLE_CYAN,    '( ^ . ^ )'), (STYLE_DEFAULT, '   Yay! Task done!')],
    [(STYLE_CYAN,    ' > w < '), (STYLE_DEFAULT, '    Good job!')],
    [(STYLE_DIM,     '     /  |  \\')],
    [(STYLE_DIM,     '    /   |   \\')],
    [(STYLE_DIM,     '   (____|____)')]
])

ART_SAD = create_art([
    [(STYLE_MAGENTA, '       /\\_/\\')],
    [(STYLE_CYAN,    '( T _ T )'), (STYLE_DEFAULT, '   Gomen! I forgot...')],
    [(STYLE_CYAN,    ' > _ < '), (STYLE_DEFAULT, '    Or maybe I lost the file?!')],
    [(STYLE_DIM,     '     /  |  \\')],
    [(STYLE_DIM,     '    /   |   \\')],
    [(STYLE_DIM,     '   (____|____)')]
])

# The dictionary that the rest of the app uses
MANAGER_CHAN_ART = {
    "idle": ART_IDLE,
    "thinking": ART_THINKING,
    "happy": ART_HAPPY,
    "sad": ART_SAD
}