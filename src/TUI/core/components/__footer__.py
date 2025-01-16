import curses

class Footer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def display(self, use_dark_mode):
        height, width = self.stdscr.getmaxyx()
        color_pair = curses.color_pair(11 if use_dark_mode else 2)
        color_pair_toggle = curses.color_pair(16 if use_dark_mode else 7)
        color_pair_error = curses.color_pair(12 if use_dark_mode else 3)

        self.stdscr.addstr(height - 1, 1, " " * (width - 2), color_pair)
        self.stdscr.addstr(
            height - 1, 1, "[^C Exit]", color_pair_error | curses.A_BOLD
        )
        prompt = "[Arrow keys Navigate] [TAB Select/Unselect]"
        self.stdscr.addstr(height - 1, width // 2 - 28, prompt, color_pair)
        self.stdscr.addstr(
            height - 1,
            width - 22,
            "[^D Toggle Dark Mode]",
            color_pair_toggle | curses.A_BOLD,
        )
