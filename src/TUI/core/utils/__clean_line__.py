class CleanLine:
    def __init__(self, stdscr):
        self.stdscr = stdscr
    
    def clean_line(self, x, y):
        self.stdscr.move(y, x)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
