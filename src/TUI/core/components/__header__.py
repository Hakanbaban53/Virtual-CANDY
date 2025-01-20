import atexit
import curses
import threading
import time
from TUI.core.static.__data__ import APP_NAME, APP_VERSION

class Header:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.update_colors()
        self.clock_text = "00:00:00"
        self.running = False
        self.clock_win = curses.newwin(1, 10, 0, stdscr.getmaxyx()[1] - 10)
        self.lock = threading.Lock()
        self.start_clock()

        atexit.register(self.stop_clock, "Goodbye!", True)
        
    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_blue = curses.color_pair(8 if DARK_MODE else 17)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def update_clock(self, text: str = None, blink: bool = False):
        while self.running and text is None:
            with self.lock:
                self.clock_text = time.strftime("%H:%M:%S")
                self.refresh_clock()
            time.sleep(1)
        if text is not None:
            with self.lock:
                self.clock_text = text
                self.refresh_clock(blink=blink)

    def refresh_clock(self, blink: bool = False):
        self.clock_win.addnstr(0, 0, self.clock_text, 8, self.color_pair_blue | curses.A_BOLD | (curses.A_BLINK if blink else 0))
        self.clock_win.refresh()

    def start_clock(self):
        self.running = True
        threading.Thread(target=self.update_clock, daemon=True).start()

    def stop_clock(self, text: str = None, blink: bool = False):
        self.running = False
        if text is not None:
            self.update_clock(text, blink)

    def display(self):
        height, width = self.stdscr.getmaxyx()
        self.update_colors()
        # Clear the header line
        self.stdscr.addstr(0, 0, " " * width, self.color_pair_blue)

        # Display version
        self.stdscr.addstr(0, 1, APP_VERSION, self.color_pair_blue | curses.A_BOLD)

        self.clock_win.addstr(0, 0, self.clock_text, self.color_pair_blue | curses.A_BOLD)

        # Display app name centered
        self.stdscr.addstr(
            0,
            (width // 2) - (len(APP_NAME) // 2),
            APP_NAME,
            self.color_pair_blue | curses.A_BOLD,
        )
        self.stdscr.refresh()