from sys import exit
from curses import napms, color_pair

from TUI.core.static.__data__ import MIN_COLS, MIN_LINES

class Errors:
    def __init__(self, stdscr):
        """
        Initialize the Errors class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = color_pair(3 if DARK_MODE else 12)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def terminal_size_error(self):
        """
        Handle terminal size errors by displaying an error message
        and exiting the program.
        """
        height, width = self.stdscr.getmaxyx()
        self.stdscr.clear()

        error_message = (
            f"Terminal size is too small. Minimum required is {MIN_LINES} rows and {MIN_COLS} columns."
        )
        x = width // 2 - len(error_message) // 2
        y = height // 2
        self.stdscr.addstr(y, x, error_message, self.color_pair_red)
        self.stdscr.refresh()
        napms(3000)
        exit(0)
