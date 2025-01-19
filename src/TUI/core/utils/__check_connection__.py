from curses import napms, color_pair, A_BOLD

from TUI.core.static.__data__ import OPTIONS_YES_NO
from core.__check_repository_connection__ import check_linux_package_manager_connection


class CheckPackageManagerConnection:
    def __init__(self, stdscr, linux_distro_id, clean_line):
        """
        Initialize the CheckPackageManagerConnection class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
        self.clean_line = clean_line
        self.linux_distro_id = linux_distro_id
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = color_pair(3 if DARK_MODE else 12)
        self.color_pair_green = color_pair(5 if DARK_MODE else 14)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def package_manager_connection(self, selections):
        height, width = self.stdscr.getmaxyx()

        while True:
            prompt_checking = "Checking Package Manager Connection"
            x = width // 2 - len(prompt_checking) // 2 - 4
            y = height // 2 + 2
            self.stdscr.addstr(y, x, prompt_checking)
            self.stdscr.refresh()

            connected = check_linux_package_manager_connection(self.linux_distro_id)

            if connected:
                self.stdscr.addstr(
                    y, x + len(prompt_checking), " [OK]", self.color_pair_green | A_BOLD
                )
                self.stdscr.refresh()
                napms(750)
                return True
            else:
                self.stdscr.addstr(
                    y,
                    x + len(prompt_checking),
                    " [ERROR]",
                    self.color_pair_red | A_BOLD,
                )
                self.stdscr.refresh()
                prompt = "Retry connection?"
                retry = selections(
                    x=width // 2,
                    y=height // 2 + 2,
                    question=prompt,
                    options=OPTIONS_YES_NO,
                )
                if retry == "No":
                    self.clean_line.clean_line(0, height // 2 + 2)
                    self.clean_line.clean_line(0, height // 2 + 6)
                    return False
                else:
                    self.clean_line.clean_line(x, y)
