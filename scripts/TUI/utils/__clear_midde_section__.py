class ClearMiddleSection:
    def __init__(self, stdscr, width, height):
        """
        Initialize the ClearMiddleSection class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
        self.width = width
        self.height = height
    
    def clear_middle_section(self):
        for y in range(1, self.height - 1):
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()