from TUI.core.static.__data__ import MIN_COLS, MIN_LINES

class ResizeHandler:
    def __init__(self, stdscr, clean_line, header, footer, errors):
        self.stdscr = stdscr
        self.clean_line = clean_line
        self.header = header
        self.footer = footer
        self.errors = errors

    def resize_handler(self):
        """
        Handle terminal resizing.
        """
        height, width = self.stdscr.getmaxyx()
        if height < MIN_LINES or width < MIN_COLS:
            self.errors.terminal_size_error()
        self.clean_line.clean_line(0, 0)
        self.clean_line.clean_line(0, height - 1)
        self.header.display()
        self.footer.display()