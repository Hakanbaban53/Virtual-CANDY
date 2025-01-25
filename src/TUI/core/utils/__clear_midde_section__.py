class ClearMiddleSection:
    def __init__(self, stdscr):
        """
        Initialize the ClearMiddleSection class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
    
    def clear_middle_section(self):
        """
        Clear the middle section of the terminal.
        """
        height, _ = self.stdscr.getmaxyx()
        for y in range(1, height - 1):
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()