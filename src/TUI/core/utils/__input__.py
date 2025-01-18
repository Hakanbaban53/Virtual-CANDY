from curses import color_pair, A_BOLD, noecho, error, echo, newwin


class Input:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = color_pair(3 if DARK_MODE else 12)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def get_user_input_string(self, prompt):
        # Modal dimensions
        height, width = 3, len(prompt) + 20

        # Center modal on screen
        y = (self.stdscr.getmaxyx()[0] - height) // 2
        x = (self.stdscr.getmaxyx()[1] - width) // 2

        # Create modal input box
        input_win = newwin(height, width, y, x)
        input_win.box()
        input_win.keypad(True)
        input_win.bkgd(self.color_pair_normal)


        # Display prompt inside modal
        echo()
        input_win.addstr(1, 2, prompt, self.color_pair_normal | A_BOLD)
        input_win.refresh()

        while True:
            try:
                # Move cursor to the input area
                input_win.move(1, len(prompt) + 3)
                input_win.clrtoeol()  # Clear any previous input

                # Get user input
                input_str = input_win.getstr(1, len(prompt) + 3, 16).decode("utf-8")
                noecho()
                return input_str.strip()
            except error:
                # Display error message inside modal
                input_win.addstr(3, 2, "Error: Invalid input.", self.color_pair_error)
                input_win.refresh()
                noecho()
