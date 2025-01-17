import curses
import threading
import time
from TUI.core.static.__data__ import APP_NAME, APP_VERSION

class Header:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.update_colors()
        self.clock_text = "00:00:00"
        self.running = True
        self.clock_thread = threading.Thread(target=self.update_clock, daemon=True)
        self.clock_thread.start()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_blue = curses.color_pair(8 if DARK_MODE else 17)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def update_clock(self):
        while self.running:
            self.clock_text = time.strftime("%H:%M:%S")
            self.refresh_clock()
            time.sleep(1)

    def display(self):
        height, width = self.stdscr.getmaxyx()
        self.update_colors()
        # Clear the header line
        self.stdscr.addstr(0, 0, " " * width, self.color_pair_blue)

        # Display version
        self.stdscr.addstr(0, 1, APP_VERSION, self.color_pair_blue | curses.A_BOLD)

        # Display clock
        self.stdscr.addstr(0, width - len(self.clock_text) - 1, self.clock_text, self.color_pair_blue | curses.A_BOLD)

        # Display app name centered
        self.stdscr.addstr(
            0,
            width // 2 - len(APP_NAME) // 2,
            APP_NAME,
            self.color_pair_blue | curses.A_BOLD | curses.A_UNDERLINE,
        )

    def refresh_clock(self):
        """
        Refresh only the clock part of the header.
        """
        height, width = self.stdscr.getmaxyx()

        # Update the clock only
        self.stdscr.addstr(0, width - len(self.clock_text) - 1, self.clock_text, self.color_pair_blue | curses.A_BOLD)
        self.stdscr.refresh()

    def stop(self):
        if self.running:
            self.running = False
            self.clock_thread.join()  # Wait for the thread to exit
