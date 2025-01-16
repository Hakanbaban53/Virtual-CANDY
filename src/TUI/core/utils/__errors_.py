from sys import exit
from curses import napms, color_pair

class Errors:
    def __init__(self, stdscr, width, height):
        """
        Initialize the Errors class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
        self.width = width
        self.height = height

    def terminal_size_error(self, min_height, min_width):
        """
        Handle terminal size errors by displaying an error message
        and exiting the program.
        """
        self.stdscr.clear()

        error_message = (
            f"Terminal size is too small. Minimum required is {min_height} rows and {min_width} columns."
        )
        x = self.width // 2 - len(error_message) // 2
        y = self.height // 2
        self.stdscr.addstr(y, x, error_message, color_pair(2))
        self.stdscr.refresh()
        napms(3000)
        exit(0)
