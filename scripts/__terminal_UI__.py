import curses
import sys

from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    identify_distribution,
)
from functions.__get_packages_data__ import PackagesJSONHandler
from scripts.TUI.components.__app_selector__ import AppSelector
from scripts.TUI.components.__footer__ import Footer
from scripts.TUI.components.__header__ import Header
from scripts.TUI.utils.__check_connection__ import CheckPackageManagerConnection
from scripts.TUI.utils.__clean_line__ import CleanLine
from scripts.TUI.utils.__clear_midde_section__ import ClearMiddleSection
from scripts.TUI.utils.__errors_ import Errors
from scripts.TUI.utils.__color_manager__ import ColorManager
from scripts.TUI.utils.__input__ import Input
from scripts.TUI.utils.__resize_handler__ import ResizeHandler
from scripts.TUI.utils.__selections__ import Selections

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]

MIN_LINES = 20
MIN_COLS = 80
MAX_DISPLAYED_PACKAGES = 15


class PackageManagerApp:
    def __init__(self, stdscr):

        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.cmd = ClearMiddleSection(self.stdscr, self.width, self.height)
        self.clean_line = CleanLine(self.stdscr)
        self.user_input = Input(self.stdscr)

        self.selected_status_array = []
        self.use_dark_mode = True
        self.known_distros = {
            "arch": ["arch"],
            "debian": ["debian"],
            "fedora": ["fedora"],
            "ubuntu": ["ubuntu"],
        }
        self.header = Header(self.stdscr, "VCANDY", "v2.4")
        self.footer = Footer(self.stdscr)
        self.errors = Errors(self.stdscr, self.width, self.height)
        self.resize_handler = ResizeHandler(self.stdscr, self.clean_line, self.header, self.footer, self.errors)
        self.selections = Selections(self.stdscr, self.resize_handler, self.clean_line, self.footer, self.header)

        ColorManager(self.stdscr).init_colors()

    def get_output_choice(self):
        try:
            prompt = "Do you want to hide complex outputs?"
            x = curses.COLS // 2 - len(prompt) // 2
            y = curses.LINES // 2 + 3
            selection = self.selections.selections(self.use_dark_mode, prompt, x, y, self.height, self.width, OPTIONS_YES_NO, MIN_COLS, MIN_LINES)

            if selection == "Yes":
                return False
            else:
                return True

        except curses.error:
            self.errors.terminal_size_error(MIN_LINES, MIN_COLS)

    def install_or_remove(self):
        try:
            prompt = "Please select the action:"
            x = self.width // 2 - len(prompt) // 2
            y = self.height // 2 - 6
            actions = self.selections.selections(self.use_dark_mode, prompt, x, y, self.height, self.width, OPTIONS_INSTALL_REMOVE, MIN_COLS, MIN_LINES)

            if actions == "install":
                linux_distro_id = identify_distribution()

                if CheckPackageManagerConnection(
                    self.stdscr,
                    self.width,
                    self.height,
                    linux_distro_id,
                    OPTIONS_YES_NO,
                    self.clean_line,
                ).package_manager_connection(linux_distro_id):
                    return "install"
                else:
                    error_message = "Package Manager not connected."
                    exit_message = "Exiting..."
                    self.stdscr.addstr(
                        self.height // 2,
                        self.width // 2 - len(error_message) // 2,
                        error_message,
                        curses.color_pair(3) | curses.A_BOLD,
                    )
                    self.stdscr.addstr(
                        self.height // 2 + 2,
                        self.width // 2 - len(exit_message) // 2,
                        exit_message,
                        curses.color_pair(3) | curses.A_BOLD,
                    )
                    self.stdscr.refresh()
                    curses.napms(1500)
                    sys.exit(0)
            elif actions == "remove":
                return "remove"

        except curses.error:
            self.errors.terminal_size_error(MIN_LINES, MIN_COLS)

    def get_linux_distro(self):
        try:
            header_message = "Getting Linux Distro:"
            self.stdscr.addstr(
                self.height // 2 - 7,
                self.width // 2 - len(header_message) // 2,
                header_message,
                curses.color_pair(4) | curses.A_BOLD | curses.A_UNDERLINE,
            )
            linux_distribution = get_linux_distribution()
            linux_distro_id = identify_distribution()

            distro_message = "Detected Linux Distro: {}".format(linux_distribution)
            id_message = "Detected Distro ID: {}".format(linux_distro_id)

            self.stdscr.addstr(
                self.height // 2 - 5,
                self.width // 2 - len(distro_message) // 2,
                distro_message,
                curses.color_pair(2),
            )
            self.stdscr.addstr(
                self.height // 2 - 4,
                self.width // 2 - len(id_message) // 2,
                id_message,
                curses.color_pair(2),
            )

            prompt = "Is that true?"
            x = self.width // 2 - len(prompt) // 2
            y = self.height // 2 - 1
            selected_option = self.selections.selections(self.use_dark_mode, prompt, x, y, self.height, self.width, OPTIONS_YES_NO, MIN_COLS, MIN_LINES)

            warning_line = self.height // 2 - 2

            if selected_option == "Yes":
                return linux_distro_id

            elif selected_option == "No":
                while True:
                    input_prompt = "Please enter the distro: "
                    linux_distribution = self.user_input.get_user_input_string(
                        self.use_dark_mode,
                        input_prompt,
                        self.height // 2 + 3,
                        self.width // 2 - len(input_prompt) // 2,
                    )
                    linux_distribution_lower = linux_distribution.lower()

                    self.clean_line.clean_line(0, self.height // 2 - 3)

                    entered_message = "Entered Linux Distro: {}".format(
                        linux_distribution
                    )
                    self.stdscr.addstr(
                        self.height // 2 - 3,
                        self.width // 2 - len(entered_message) // 2,
                        entered_message,
                        curses.color_pair(2),
                    )

                    for distro, keywords in self.known_distros.items():
                        if any(
                            keyword in linux_distribution_lower for keyword in keywords
                        ):
                            self.clean_line.clean_line(
                                0,
                                warning_line,
                            )
                            return distro

                    warning_message = "{} distro not found. Please try again.".format(
                        linux_distribution
                    )
                    self.clean_line.clean_line(0, warning_line)
                    self.stdscr.addstr(
                        warning_line,
                        self.width // 2 - len(warning_message) // 2,
                        warning_message,
                        curses.color_pair(2) | curses.A_BOLD,
                    )
                    self.clean_line.clean_line(0, self.height // 2 + 3)

        except curses.error:
            self.errors.terminal_size_error(MIN_LINES, MIN_COLS)

    def initialize_selected_status(self, length):
        # Initialize selected status array
        return [False] * length

    def packages(self, linux_distro):
        handler = PackagesJSONHandler()
        instructions_data = handler.load_json_data()

        if linux_distro in instructions_data:
            package_list = instructions_data[linux_distro]
            relevant_packages = [package.get("name", "") for package in package_list]
            return relevant_packages
        else:
            return []

    def main(self):
        try:
            curses.curs_set(0)
            if curses.LINES < MIN_LINES or curses.COLS < MIN_COLS:
                self.errors.terminal_size_error(MIN_LINES, MIN_COLS)

            self.header.display(self.use_dark_mode)
            self.footer.display(self.use_dark_mode)

            linux_distribution = self.get_linux_distro()
            output = self.get_output_choice()

            self.cmd.clear_middle_section()
            action = self.install_or_remove()

            relevant_packages = self.packages(linux_distribution)
            self.selected_status_array = self.initialize_selected_status(
                len(relevant_packages)
            )

            AppSelector(
                self.stdscr,
                relevant_packages,
                self.width,
                self.height,
                self.use_dark_mode,
                self.cmd,
                self.selections,
                self.header,
                self.footer,
                self.resize_handler,
            ).select_app(
                relevant_packages,
                self.selected_status_array,
                action,
                linux_distribution,
                output,
                OPTIONS_YES_NO,
                MIN_COLS,
                MIN_LINES,
                MAX_DISPLAYED_PACKAGES
            )


        except curses.error:
            self.errors.terminal_size_error(MIN_LINES, MIN_COLS)

        except Exception as e:
            curses.reset_prog_mode()
            self.stdscr.clear()
            self.stdscr.addstr(1, 1, str(e), curses.color_pair(3) | curses.A_BOLD)
            self.stdscr.addstr(2, 1, "[Press any key to exit program]")
            self.stdscr.getch()
            curses.reset_shell_mode()
            sys.exit(0)


def start_terminal_ui():
    try:
        curses.wrapper(lambda stdscr: PackageManagerApp(stdscr).main())
    except KeyboardInterrupt:
        stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.clear()
        stdscr.addstr(
            curses.LINES // 2 - 2,
            curses.COLS // 2 - 14,
            "Ctrl + C pressed. Exiting...",
            curses.color_pair(3) | curses.A_BOLD,
        )
        stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 3, "Bye 👋")
        stdscr.refresh()
        curses.napms(1500)
        curses.endwin()
        sys.exit(0)
