import curses
import sys

from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)
from functions.__get_packages_data__ import PackagesJSONHandler
from scripts.TUI.components.__footer__ import Footer
from scripts.TUI.components.__header__ import Header
from scripts.TUI.components.__print_apps__ import PrintApps
from scripts.TUI.utils.__check_connection__ import CheckPackageManagerConnection
from scripts.TUI.utils.__clear_midde_section__ import ClearMiddleSection
from scripts.TUI.utils.__errors_ import Errors
from scripts.TUI.utils.__color_manager__ import ColorManager

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]

DEFAULT_HEADER = "VCANDY"
VERSION = "v2.4"
MIN_LINES = 20
MIN_COLS = 80

class PackageManagerApp:
    def __init__(self, stdscr):

        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.cmd = ClearMiddleSection(self.stdscr, self.width, self.height)

        self.selected_status_array = []
        self.use_dark_mode = True
        self.known_distros = {
            "arch": ["arch"],
            "debian": ["debian"],
            "fedora": ["fedora"],
            "ubuntu": ["ubuntu"],
        }
        self.header = Header(
            self.stdscr, "VCANDY", "v2.4"
        )
        self.footer = Footer(self.stdscr)
        self.errors = Errors(self.stdscr, self.width, self.height)

        ColorManager(self.stdscr).init_colors()

    def resize_handler(self):
        self.height, self.width = self.stdscr.getmaxyx()
        if self.height < MIN_LINES or self.width < MIN_COLS:
            self.terminal_size_error()
        self.clean_line(0, 0)
        self.clean_line(0, self.height - 1)
        self.header.display(self.use_dark_mode)
        self.footer.display(self.use_dark_mode)

    def clean_line(self, x, y):
        self.stdscr.move(y, x)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()


    def package_manager_connection(self, linux_distro_id):
        handler = CheckPackageManagerConnection(
            self.stdscr,
            self.width,
            self.height,
            linux_distro_id,
            OPTIONS_YES_NO,
        )
        return handler.package_manager_connection(self.use_dark_mode)

    def print_menu(self, selected_row, relevant_packages, selected_status):
        PrintApps(self.stdscr, self.use_dark_mode, self.width, self.height).print_menu(
            selected_row, relevant_packages, selected_status
        )

    def terminal_size_error(self):
        # Handle terminal size errors
        self.errors.terminal_size_error(MIN_LINES, MIN_COLS)        

    def get_user_input_string(self, prompt, y, x):
        color_pair = (
            curses.color_pair(2) if self.use_dark_mode else curses.color_pair(11)
        )
        color_pair_error = (
            curses.color_pair(3) if self.use_dark_mode else curses.color_pair(12)
        )
        # Get user input string
        curses.echo()
        self.stdscr.addstr(y, x, prompt, color_pair | curses.A_BOLD)
        self.stdscr.refresh()
        while True:
            try:
                input_str = self.stdscr.getstr().decode("utf-8")
                curses.noecho()
                return input_str.strip()
            except curses.error:
                self.stdscr.addstr(
                    y + 1, x + 1, "Error: Invalid input.", color_pair_error
                )
                self.stdscr.refresh()
                curses.noecho()

    def selections(self, prompt, x, y, options):
        # Handle user selections
        selected_option = 0

        while True:
            # Clear previous prompt
            self.clean_line(x, y)

            # Display prompt centered horizontally
            prompt_x = self.width // 2 - len(prompt) // 2
            self.stdscr.addstr(
                y,
                prompt_x,
                prompt,
                curses.color_pair(2) | curses.A_BOLD | curses.A_UNDERLINE,
            )

            # Calculate the starting x position to center the options
            total_options_width = (
                sum(len(option) + 4 for option in options) + (len(options) - 1) * 2
            )
            options_x = self.width // 2 - total_options_width // 2

            for i, option in enumerate(options):
                option_x = options_x + (len(option) + 6) * i
                option_y = y + 2
                if i == selected_option:
                    self.stdscr.addstr(
                        option_y, option_x, "[" + option + "]", curses.A_REVERSE
                    )
                else:
                    self.stdscr.addstr(option_y, option_x, "[" + option + "]")

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_LEFT:
                selected_option = (selected_option - 1) % len(options)
            elif key == curses.KEY_RIGHT:
                selected_option = (selected_option + 1) % len(options)
            elif key in [curses.KEY_ENTER, 10, 13]:
                return options[selected_option]
            elif key == 4:  # Ctrl + D for toggle dark/light mode
                self.use_dark_mode = not self.use_dark_mode
                self.stdscr.bkgd(
                    curses.color_pair(2)
                    if self.use_dark_mode
                    else curses.color_pair(11)
                )
                self.stdscr.refresh()
                self.header.display(self.use_dark_mode)
                self.footer.display(self.use_dark_mode)
            elif key == curses.KEY_RESIZE:
                self.resize_handler()

    def get_output_choice(self):
        try:
            prompt = "Do you want to hide complex outputs?"
            x = curses.COLS // 2 - len(prompt) // 2
            y = curses.LINES // 2 + 3
            selection = self.selections(prompt, x, y, OPTIONS_YES_NO)

            if selection == "Yes":
                return False
            else:
                return True

        except curses.error:
            self.terminal_size_error()

    def install_or_remove(self):
        try:
            prompt = "Please select the action:"
            x = self.width // 2 - len(prompt) // 2
            y = self.height // 2 - 6
            actions = self.selections(prompt, x, y, OPTIONS_INSTALL_REMOVE)

            if actions == "install":
                linux_distro_id = identify_distribution()

                if self.package_manager_connection(linux_distro_id):
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
            self.terminal_size_error()

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
            selected_option = self.selections(prompt, x, y, OPTIONS_YES_NO)

            warning_line = (
                self.height // 2 - 2
            )

            if selected_option == "Yes":
                return linux_distro_id

            elif selected_option == "No":
                while True:
                    input_prompt = "Please enter the distro: "
                    linux_distribution = self.get_user_input_string(
                        input_prompt,
                        self.height // 2 + 3,
                        self.width // 2 - len(input_prompt) // 2,
                    )
                    linux_distribution_lower = linux_distribution.lower()

                    self.clean_line(0, self.height // 2 - 3)

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
                            self.clean_line(
                                0,
                                warning_line,
                            )
                            return distro

                    warning_message = "{} distro not found. Please try again.".format(
                        linux_distribution
                    )
                    self.clean_line(0, warning_line)
                    self.stdscr.addstr(
                        warning_line,
                        self.width // 2 - len(warning_message) // 2,
                        warning_message,
                        curses.color_pair(2) | curses.A_BOLD,
                    )
                    self.clean_line(0, self.height // 2 + 3)

        except curses.error:
            self.terminal_size_error()

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
                self.terminal_size_error()

            color_pair = (
                curses.color_pair(8) if self.use_dark_mode else curses.color_pair(16)
            )

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

            self.cmd.clear_middle_section()
            self.print_menu(0, relevant_packages, self.selected_status_array)
            current_row = 0

            while True:
                key = self.stdscr.getch()

                if key == curses.KEY_DOWN:
                    current_row = (current_row + 1) % len(relevant_packages)

                elif key == curses.KEY_UP:
                    current_row = (current_row - 1) % len(relevant_packages)

                elif key == 9:  # TAB key
                    self.selected_status_array[current_row] = (
                        not self.selected_status_array[current_row]
                    )

                elif key == 10:  # Enter key
                    self.cmd.clear_middle_section()
                    selected_entities = [
                        status
                        for idx, status in enumerate(relevant_packages)
                        if self.selected_status_array[idx]
                    ]

                    if not selected_entities:
                        self.stdscr.addstr(
                            curses.LINES // 2,
                            curses.COLS // 2 - 12,
                            "Please select packages!",
                            curses.color_pair(3) | curses.A_BOLD,
                        )
                        self.stdscr.addstr(
                            curses.LINES // 2 + 2,
                            curses.COLS // 2 - 17,
                            "[Press any arrow key to continue]",
                        )
                        continue

                    prompt_selected = "Selected applications:"
                    self.stdscr.addstr(
                        2,
                        curses.COLS // 2 - len(prompt_selected) // 2,
                        prompt_selected,
                        curses.color_pair(6) | curses.A_BOLD,
                    )

                    for idx, entity in enumerate(selected_entities):
                        self.stdscr.addstr(
                            3 + idx,
                            curses.COLS // 2 - len(entity) // 2,
                            entity,
                        )

                    prompt = "Do you want to continue?"
                    x = curses.COLS // 2 - len(prompt) // 2
                    y = 4 + len(selected_entities)
                    selection = self.selections(prompt, x, y, OPTIONS_YES_NO)

                    if selection == "Yes":
                        curses.reset_shell_mode()

                        for idx, entity in enumerate(selected_entities):
                            self.stdscr.clear()
                            action_message = f"{entity} {action}ing...\n"
                            self.stdscr.addstr(
                                1,
                                0,
                                action_message,
                                color_pair | curses.A_BOLD | curses.A_UNDERLINE,
                            )
                            self.stdscr.refresh()
                            get_linux_package_manager(
                                linux_distribution, entity, output, action
                            )
                            curses.napms(1500)

                        curses.reset_prog_mode()
                        self.stdscr.clear()
                        self.header.display(self.use_dark_mode)
                        self.footer.display(self.use_dark_mode)

                        success_message = "The selected options have been implemented!"
                        reboot_message = "Reboot for the installed apps to appear in the app menu and work properly!"
                        press_any_key = "[Press any key to exit]"
                        self.stdscr.addstr(
                            curses.LINES // 2 - 4,
                            curses.COLS // 2 - len(success_message) // 2,
                            success_message,
                        )
                        self.stdscr.addstr(
                            curses.LINES // 2 - 2,
                            curses.COLS // 2 - len(reboot_message) // 2,
                            reboot_message,
                        )
                        self.stdscr.addstr(
                            curses.LINES // 2,
                            curses.COLS // 2 - len(press_any_key) // 2,
                            press_any_key,
                            color_pair | curses.A_BOLD,
                        )
                        self.stdscr.getch()
                        break

                elif key == 4:  # Ctrl + D for toggle dark/light mode
                    self.use_dark_mode = not self.use_dark_mode
                    self.stdscr.bkgd(
                        curses.color_pair(2)
                        if self.use_dark_mode
                        else curses.color_pair(11)
                    )
                    self.stdscr.refresh()
                    self.header.display(self.use_dark_mode)
                    self.footer.display(self.use_dark_mode)
                    self.print_menu(
                        current_row, relevant_packages, self.selected_status_array
                    )
                elif key == curses.KEY_RESIZE:
                    self.resize_handler()

                self.print_menu(
                    current_row, relevant_packages, self.selected_status_array
                )

        except curses.error:
            self.terminal_size_error()

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
