import curses

class ColorInit:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def init_colors(self):
        curses.start_color()

        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(curses.COLOR_BLACK, 0, 0, 0)

        dark_mode_colors = [
            (2, curses.COLOR_WHITE, curses.COLOR_BLACK), # White on black
            (3, curses.COLOR_RED, curses.COLOR_BLACK), # Red on black
            (4, curses.COLOR_CYAN, curses.COLOR_BLACK), # Cyan on black
            (5, curses.COLOR_GREEN, curses.COLOR_BLACK), # Green on black
            (6, curses.COLOR_YELLOW, curses.COLOR_BLACK), # Yellow on black
            (7, curses.COLOR_MAGENTA, curses.COLOR_BLACK), # Magenta on black
            (8, curses.COLOR_BLUE, curses.COLOR_WHITE), # Blue on white
            (9, curses.COLOR_WHITE, curses.COLOR_BLUE), # White on blue
        ]
        
        light_mode_colors = [
            (11, curses.COLOR_BLACK, curses.COLOR_WHITE), # Black on white
            (12, curses.COLOR_RED, curses.COLOR_WHITE), # Red on white
            (13, curses.COLOR_CYAN, curses.COLOR_WHITE), # Cyan on white
            (14, curses.COLOR_GREEN, curses.COLOR_WHITE),  # Green on white
            (15, curses.COLOR_YELLOW, curses.COLOR_WHITE), # Yellow on white
            (16, curses.COLOR_MAGENTA, curses.COLOR_WHITE), # Magenta on white
            (17, curses.COLOR_BLUE, curses.COLOR_BLACK), # Blue on black
            (18, curses.COLOR_BLACK, curses.COLOR_BLUE), # Black on blue
        ]

        for color in dark_mode_colors:
            curses.init_pair(*color)
        for color in light_mode_colors:
            curses.init_pair(*color)