import time

import pyfiglet
from rich.color import Color
from rich.progress import track
from rich.style import Style
from rich.text import Text

from . import console  # Import the shared console instance from __init__.py


def _create_gradient_text(ascii_art: str, start_rgb: tuple, end_rgb: tuple) -> Text:
    """
    Applies a vertical color gradient to a multi-line string of ASCII art.
    This is a helper function internal to this module.
    """
    rich_text = Text()
    lines = ascii_art.splitlines()
    num_lines = len(lines)

    for i, line in enumerate(lines):
        # Calculate the color for the current line by interpolating
        ratio = i / (num_lines - 1) if num_lines > 1 else 0

        r = int(start_rgb[0] * (1 - ratio) + end_rgb[0] * ratio)
        g = int(start_rgb[1] * (1 - ratio) + end_rgb[1] * ratio)
        b = int(start_rgb[2] * (1 - ratio) + end_rgb[2] * ratio)

        line_style = Style(color=Color.from_rgb(r, g, b))

        rich_text.append(line, style=line_style)
        if i < num_lines - 1:
            rich_text.append("\n")

    return rich_text


def display_banner():
    """
    Generates and prints the 'pydo' ASCII art banner to the console.
    This is the main function to be called from other parts of the application.
    """
    # 1. Generate the ASCII art text using pyfiglet
    ascii_art_str = pyfiglet.figlet_format("pydo", font="slant")

    # 2. Define start and end colors for the gradient
    start_color = (0, 135, 255)  # Blue
    end_color = (200, 50, 255)  # Purple/Magenta

    # 3. Create the gradient Text object
    gradient_art = _create_gradient_text(ascii_art_str, start_color, end_color)

    # 4. Print the final result to the console
    console.print(gradient_art)


def run_init_animation():
    """
    Displays the banner and a fake progress bar to simulate initialization.
    """
    display_banner()

    total_duration_seconds = 2
    steps = 100
    sleep_per_step = total_duration_seconds / steps

    # Use rich.progress.track to show a simple progress bar
    for _ in track(range(steps), description="[cyan]Configuring pydo environment...\n"):
        time.sleep(sleep_per_step)
