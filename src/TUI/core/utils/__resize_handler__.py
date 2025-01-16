class ResizeHandler:
    def __init__(self, stdscr, clean_line, header, footer, errors):
        self.stdscr = stdscr
        self.clean_line = clean_line
        self.header = header
        self.footer = footer
        self.errors = errors

    def resize_handler(self, use_dark_mode, width, height, MIN_COLS, MIN_LINES):
        if height < MIN_LINES or width < MIN_COLS:
            self.errors.terminal_size_error()
        self.clean_line.clean_line(0, 0)
        self.clean_line.clean_line(0, height - 1)
        self.header.display(use_dark_mode)
        self.footer.display(use_dark_mode)