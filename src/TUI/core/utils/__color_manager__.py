import curses

class ColorManager:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def init_colors(self, dark_mode=True):
        curses.start_color()

        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(curses.COLOR_BLACK, 0, 0, 0)

        dark_mode_colors = [
            (2, curses.COLOR_WHITE, curses.COLOR_BLACK),
            (3, curses.COLOR_RED, curses.COLOR_BLACK),
            (4, curses.COLOR_CYAN, curses.COLOR_BLACK),
            (5, curses.COLOR_GREEN, curses.COLOR_BLACK),
            (6, curses.COLOR_YELLOW, curses.COLOR_BLACK),
            (7, curses.COLOR_MAGENTA, curses.COLOR_BLACK),
            (8, curses.COLOR_BLUE, curses.COLOR_WHITE),
            (9, curses.COLOR_WHITE, curses.COLOR_BLUE),
        ]
        
        light_mode_colors = [
            (11, curses.COLOR_BLACK, curses.COLOR_WHITE),
            (12, curses.COLOR_RED, curses.COLOR_WHITE),
            (13, curses.COLOR_CYAN, curses.COLOR_WHITE),
            (14, curses.COLOR_GREEN, curses.COLOR_WHITE),
            (15, curses.COLOR_YELLOW, curses.COLOR_WHITE),
            (16, curses.COLOR_MAGENTA, curses.COLOR_WHITE),
            (17, curses.COLOR_BLUE, curses.COLOR_BLACK),
            (18, curses.COLOR_WHITE, curses.COLOR_BLUE),
        ]

        for color in dark_mode_colors:
            curses.init_pair(*color)
        for color in light_mode_colors:
            curses.init_pair(*color)