import curses

class Modal:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def draw_modal(self, title, content):
        """Draws a modal and returns its window object."""
        height, width = self.stdscr.getmaxyx()

        # Modal dimensions
        modal_width = max(len(title), max(len(line) for line in content)) + 4
        modal_height = len(content) + 4
        modal_x = (width - modal_width) // 2
        modal_y = (height - modal_height) // 2

        # Draw modal box
        modal_win = curses.newwin(modal_height, modal_width, modal_y, modal_x)
        modal_win.box()

        # Draw title (centered at the top)
        title_x = (modal_width - len(title)) // 2
        modal_win.addstr(0, title_x, title, curses.A_BOLD)

        # Draw content
        for idx, line in enumerate(content):
            modal_win.addstr(2 + idx, 2, line)

        modal_win.refresh()
        return modal_win
