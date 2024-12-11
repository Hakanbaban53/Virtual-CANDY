import curses

class Header:
    def __init__(self, stdscr, default_header, version):
        self.stdscr = stdscr
        self.default_header = default_header
        self.version = version

    def display(self, use_dark_mode):
        height, width = self.stdscr.getmaxyx()
        color_pair = curses.color_pair(8 if use_dark_mode else 17)

        self.stdscr.addstr(0, 0, " " * width, color_pair)
        self.stdscr.addstr(0, 1, self.version, color_pair | curses.A_BOLD)
        self.stdscr.addstr(
            0,
            width // 2 - len(self.default_header) // 2,
            self.default_header,
            color_pair | curses.A_BOLD | curses.A_UNDERLINE,
        )
