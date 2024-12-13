from curses import color_pair, A_BOLD, noecho, error, echo

class Input:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        
    def get_user_input_string(self, use_dark_mode, prompt, y, x):
        color_pair_normal = (
            color_pair(2) if use_dark_mode else color_pair(11)
        )
        color_pair_error = (
            color_pair(3) if use_dark_mode else color_pair(12)
        )
        # Get user input string
        echo()
        self.stdscr.addstr(y, x, prompt, color_pair_normal | A_BOLD)
        self.stdscr.refresh()
        while True:
            try:
                input_str = self.stdscr.getstr().decode("utf-8")
                noecho()
                return input_str.strip()
            except error:
                self.stdscr.addstr(
                    y + 1, x + 1, "Error: Invalid input.", color_pair_error
                )
                self.stdscr.refresh()
                noecho()