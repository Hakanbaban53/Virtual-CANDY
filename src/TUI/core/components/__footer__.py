import curses
from TUI.core.static.__data__ import FOOTER_TEXT

class Footer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_magenta = curses.color_pair(7 if DARK_MODE else 16)
        self.color_pair_blue = curses.color_pair(8 if DARK_MODE else 17)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def display(self):
        height, width = self.stdscr.getmaxyx()
        self.update_colors()
        self.stdscr.addstr(height - 1, 1, " " * (width - 2), self.color_pair_normal | curses.A_REVERSE)
        self.stdscr.addstr(height - 1, 1, FOOTER_TEXT[0], self.color_pair_red | curses.A_BOLD | curses.A_REVERSE)
        self.stdscr.addstr(height - 1, width - len(FOOTER_TEXT[1]) - 1, FOOTER_TEXT[1], self.color_pair_magenta | curses.A_BOLD | curses.A_REVERSE)
