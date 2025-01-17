import curses
import sys

from TUI.core.components.__app_selector__ import AppSelector
from TUI.core.components.__footer__ import Footer
from TUI.core.components.__header__ import Header
from TUI.core.static.__color_init__ import ColorInit
from TUI.core.static.__data__ import DARK_MODE, KNOWN_DISTROS, OPTIONS_INSTALL_REMOVE, OPTIONS_YES_NO
from TUI.core.utils.__check_connection__ import CheckPackageManagerConnection
from TUI.core.utils.__clean_line__ import CleanLine
from TUI.core.utils.__clear_midde_section__ import ClearMiddleSection
from TUI.core.utils.__errors_ import Errors
from TUI.core.utils.__input__ import Input
from TUI.core.utils.__resize_handler__ import ResizeHandler
from TUI.core.utils.__selections__ import Selections

class PackageManagerApp:
    def __init__(
        self, stdscr, linux_distro_id, linux_distro_pretty_name, instructions_data
    ):

        self.stdscr = stdscr
        self.linux_distro_id = linux_distro_id
        self.linux_distro_pretty_name = linux_distro_pretty_name
        self.instructions_data = instructions_data

        self.height, self.width = self.stdscr.getmaxyx()

        ColorInit(self.stdscr).init_colors()
        
        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_cyan = curses.color_pair(4 if DARK_MODE else 13)

        self.cmd = ClearMiddleSection(self.stdscr)
        self.clean_line = CleanLine(self.stdscr)
        self.user_input = Input(self.stdscr)

        self.selected_status_array = []

        self.header = Header(self.stdscr)
        self.footer = Footer(self.stdscr)
        self.errors = Errors(self.stdscr)
        self.resize_handler = ResizeHandler(
            self.stdscr, self.clean_line, self.header, self.footer, self.errors
        )
        self.selections = Selections(
            self.stdscr, self.resize_handler, self.clean_line, self.footer, self.header
        )


    def get_output_choice(self):
        try:
            prompt = "Do you want to hide complex outputs?"
            x = curses.COLS // 2 - len(prompt) // 2
            y = curses.LINES // 2 + 3
            selection = self.selections.selections(
                prompt,
                x,
                y,
                OPTIONS_YES_NO,
            )

            if selection == "Yes":
                return False
            else:
                return True

        except curses.error:
            self.errors.terminal_size_error()

    def install_or_remove(self):
        try:
            prompt = "Please select the action:"
            x = self.width // 2 - len(prompt) // 2
            y = self.height // 2 - 6
            actions = self.selections.selections(
                prompt,
                x,
                y,
                OPTIONS_INSTALL_REMOVE,
            )

            if actions == "install":

                if CheckPackageManagerConnection(
                    self.stdscr,
                    self.linux_distro_id,
                    self.clean_line,
                ).package_manager_connection(self.selections.selections):
                    return "install"
                else:
                    error_message = "Package Manager not connected."
                    exit_message = "Exiting..."
                    self.stdscr.addstr(
                        self.height // 2,
                        self.width // 2 - len(error_message) // 2,
                        error_message,
                        self.color_pair_red | curses.A_BOLD,
                    )
                    self.stdscr.addstr(
                        self.height // 2 + 2,
                        self.width // 2 - len(exit_message) // 2,
                        exit_message,
                        self.color_pair_red | curses.A_BOLD,
                    )
                    self.stdscr.refresh()
                    curses.napms(1500)
                    sys.exit(0)
            elif actions == "remove":
                return "remove"

        except curses.error:
            self.errors.terminal_size_error()

    def get_linux_distro(self):
        try:
            header_message = "Getting Linux Distro:"
            self.stdscr.addstr(
                self.height // 2 - 7,
                self.width // 2 - len(header_message) // 2,
                header_message,
                self.color_pair_cyan | curses.A_BOLD | curses.A_UNDERLINE,
            )
            linux_distribution = self.linux_distro_pretty_name
            linux_distro_id = self.linux_distro_id

            distro_message = "Detected Linux Distro: {}".format(linux_distribution)
            id_message = "Detected Distro ID: {}".format(linux_distro_id)

            self.stdscr.addstr(
                self.height // 2 - 5,
                self.width // 2 - len(distro_message) // 2,
                distro_message,
                self.color_pair_normal,
            )
            self.stdscr.addstr(
                self.height // 2 - 4,
                self.width // 2 - len(id_message) // 2,
                id_message,
                self.color_pair_normal,
            )

            prompt = "Is that true?"
            x = self.width // 2 - len(prompt) // 2
            y = self.height // 2 - 1
            selected_option = self.selections.selections(
                prompt,
                x,
                y,
                OPTIONS_YES_NO,
            )

            warning_line = self.height // 2 - 2

            if selected_option == "Yes":
                return linux_distro_id

            elif selected_option == "No":
                while True:
                    input_prompt = "Please enter the distro: "
                    linux_distribution = self.user_input.get_user_input_string(
                        input_prompt
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
                        self.color_pair_normal,
                    )

                    for distro, keywords in KNOWN_DISTROS.items():
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
                        self.color_pair_red | curses.A_BOLD,
                    )
                    self.clean_line.clean_line(0, self.height // 2 + 3)

        except curses.error:
            self.errors.terminal_size_error()

    def initialize_selected_status(self, length):
        # Initialize selected status array
        return [False] * length

    def packages(self, linux_distro):
        instructions_data = self.instructions_data

        if linux_distro in instructions_data:
            package_list = instructions_data[linux_distro]
            relevant_packages = [package.get("name", "") for package in package_list]
            return relevant_packages
        else:
            return []

    def main(self):
        try:
            curses.curs_set(0)
            self.resize_handler.resize_handler()

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
            )

        except curses.error:
            self.errors.terminal_size_error()

        except Exception as e:
            curses.reset_prog_mode()
            self.stdscr.clear()
            self.stdscr.addstr(1, 1, str(e), self.color_pair_red | curses.A_BOLD)
            self.stdscr.addstr(2, 1, "[Press any key to exit program]")
            self.stdscr.getch()
            curses.reset_shell_mode()
            sys.exit(0)


def start_terminal_ui(linux_distro_id, linux_distro_pretty_name, instructions_data):
    try:
        curses.wrapper(
            lambda stdscr: PackageManagerApp(
                stdscr,
                linux_distro_id=linux_distro_id,
                linux_distro_pretty_name=linux_distro_pretty_name,
                instructions_data=instructions_data,
            ).main()
        )
    except KeyboardInterrupt:
        stdscr = curses.initscr()

        curses.start_color()
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.clear()
        stdscr.addstr(
            curses.LINES // 2 - 2,
            curses.COLS // 2 - 14,
            "Ctrl + C pressed. Exiting...",
            curses.color_pair(3 if DARK_MODE else 12) | curses.A_BOLD,
        )
        stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 3, "Bye 👋")
        Header(stdscr).stop()
        curses.endwin()
        sys.exit(0)
