import curses


class Modal:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.modal_win = None  # Current modal window
        self.modal_pad = None
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_magenta = curses.color_pair(7 if DARK_MODE else 16)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def draw_modal(self, title, content, hint="Press ESC to close", long_content=[]):
        """Display a modal dialog with the given title and content."""
        height, width = self.stdscr.getmaxyx()

        # Modal dimensions
        modal_width = max(len(title), max(len(line) for line in content)) + 4
        modal_height = len(content) + 5 + (10 if long_content else 0)
        modal_x = (width - modal_width) // 2
        modal_y = (height - modal_height) // 2

        # Create and render modal window
        self.modal_win = curses.newwin(modal_height, modal_width, modal_y, modal_x)
        self.modal_win.box()
        self.modal_win.bkgd(self.color_pair_normal)

        if long_content:
            self.modal_pad = curses.newpad(len(long_content) + 1, modal_width * 400)
            self.modal_pad.bkgd(self.color_pair_normal | curses.A_REVERSE)
            for idx, line in enumerate(long_content):
                self.modal_pad.addstr(idx, 0, line)
            self.modal_win.refresh()
            

        # Draw title
        title_x = (modal_width - len(title)) // 2
        self.modal_win.addstr(0, title_x, title, self.color_pair_yellow | curses.A_BOLD | curses.A_UNDERLINE | curses.A_REVERSE)

        # Draw content
        for idx, line in enumerate(content):
            self.modal_win.addstr(2 + idx, 2, line)

        # Draw exit hint
        self.modal_win.addstr(modal_height - 2, 2, hint, self.color_pair_magenta | curses.A_REVERSE | curses.A_BOLD)
        self.modal_win.refresh()

    def close(self):
        """Clear the modal window."""
        self.modal_win.clear()
        self.modal_win.refresh()
        self.modal_win = None
