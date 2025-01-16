from curses import napms, color_pair, A_BOLD

from core.__check_repository_connection__ import check_linux_package_manager_connection


class CheckPackageManagerConnection:
    def __init__(self, stdscr, width, height, linux_distro_id, OPTIONS_YES_NO, clean_line):
        """
        Initialize the CheckPackageManagerConnection class with the stdscr object and dimensions.
        """
        self.stdscr = stdscr
        self.clean_line = clean_line
        self.width = width
        self.height = height
        self.linux_distro_id = linux_distro_id
        self.OPTIONS_YES_NO = OPTIONS_YES_NO

    def package_manager_connection(self, use_dark_mode):
        color_pair_success = color_pair(5 if use_dark_mode else 14)
        color_pair_error = color_pair(3 if use_dark_mode else 12)

        while True:
            prompt_checking = "Checking Package Manager Connection"
            x = self.width // 2 - len(prompt_checking) // 2 - 4
            y = self.height // 2 - 2
            self.stdscr.addstr(y, x, prompt_checking)
            self.stdscr.refresh()

            connected = check_linux_package_manager_connection(self.linux_distro_id)

            if connected:
                self.stdscr.addstr(
                    y, x + len(prompt_checking), " [OK]", color_pair_success | A_BOLD
                )
                self.stdscr.refresh()
                napms(750)
                return True
            else:
                self.stdscr.addstr(
                    y,
                    x + len(prompt_checking),
                    " [ERROR]",
                    color_pair_error | A_BOLD,
                )
                self.stdscr.refresh()
                prompt = "Retry connection?"
                # retry = selections(
                #     prompt, self.width // 2, self.height // 2, self.OPTIONS_YES_NO
                # )
                # if retry == "No":
                self.clean_line.clean_line(0, self.height // 2)
                self.clean_line.clean_line(0, self.height // 2 + 2)
                return False
                # else:
                #     self.clean_line.clean_line(x, y)
        