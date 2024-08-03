import curses
import sys
from functions.__check_repository_connection__ import (
    check_linux_package_manager_connection,
)
from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)
from functions.__get_packages_data__ import PackagesJSONHandler

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]
MAX_DISPLAYED_PACKAGES = 15
DEFAULT_HEADER = "VCANDY"
VERSION = "v2.2"
MIN_LINES = 20
MIN_COLS = 80

class PackageManagerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.selected_status_array = []
        self.use_dark_mode = True
        self.known_distros = {
            "arch": ["arch"],
            "debian": ["debian"],
            "fedora": ["fedora"],
            "ubuntu": ["ubuntu"],
        }
        self.init_colors()

    def init_colors(self):
        curses.start_color()
        CUSTOM_COLOR_WHITE = 255
        CUSTOM_COLOR_BLACK = 0

        curses.init_color(CUSTOM_COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(CUSTOM_COLOR_BLACK, 0, 0, 0)

        dark_mode_colors = [
            (1, CUSTOM_COLOR_WHITE, CUSTOM_COLOR_BLACK),
            (2, curses.COLOR_RED, CUSTOM_COLOR_BLACK),
            (3, curses.COLOR_CYAN, CUSTOM_COLOR_BLACK),
            (4, curses.COLOR_GREEN, CUSTOM_COLOR_BLACK),
            (5, curses.COLOR_YELLOW, CUSTOM_COLOR_BLACK),
            (6, curses.COLOR_MAGENTA, CUSTOM_COLOR_BLACK),
            (7, curses.COLOR_BLUE, CUSTOM_COLOR_WHITE),
            (8, CUSTOM_COLOR_WHITE, curses.COLOR_BLUE),
        ]

        light_mode_colors = [
            (11, CUSTOM_COLOR_BLACK, CUSTOM_COLOR_WHITE),
            (12, curses.COLOR_RED, CUSTOM_COLOR_WHITE),
            (13, curses.COLOR_CYAN, CUSTOM_COLOR_WHITE),
            (14, curses.COLOR_GREEN, CUSTOM_COLOR_WHITE),
            (15, curses.COLOR_YELLOW, CUSTOM_COLOR_WHITE),
            (16, curses.COLOR_MAGENTA, CUSTOM_COLOR_WHITE),
            (17, curses.COLOR_BLUE, CUSTOM_COLOR_BLACK),
            (18, CUSTOM_COLOR_WHITE, curses.COLOR_BLUE),
        ]

        for color in dark_mode_colors:
            curses.init_pair(*color)
        for color in light_mode_colors:
            curses.init_pair(*color)

    def display_header(self):
        color_pair = curses.color_pair(7 if self.use_dark_mode else 17)
        self.stdscr.addstr(0, 0, " " * self.width, color_pair)
        self.stdscr.addstr(0, 1, VERSION, color_pair | curses.A_BOLD)
        self.stdscr.addstr(
            0,
            self.width // 2 - len(DEFAULT_HEADER) // 2,
            DEFAULT_HEADER,
            color_pair | curses.A_BOLD | curses.A_UNDERLINE,
        )

    def display_footer(self):
        color_pair = curses.color_pair(11 if self.use_dark_mode else 1)
        color_pair_toggle = curses.color_pair(16 if self.use_dark_mode else 6)
        color_pair_error = curses.color_pair(12 if self.use_dark_mode else 2)
        self.stdscr.addstr(self.height - 1, 1, " " * (self.width - 2), color_pair)
        self.stdscr.addstr(
            self.height - 1, 1, "[^C Exit]", color_pair_error | curses.A_BOLD
        )
        prompt = "[Arrow keys Navigate] [TAB Select/Unselect]"
        self.stdscr.addstr(self.height - 1, self.width // 2 - 28, prompt, color_pair)
        self.stdscr.addstr(
            self.height - 1,
            self.width - 22,
            "[^D Toggle Dark Mode]",
            color_pair_toggle | curses.A_BOLD,
        )

    def resize_handler(self):
        self.height, self.width = self.stdscr.getmaxyx()
        if self.height < MIN_LINES or self.width < MIN_COLS:
            self.terminal_size_error()
        self.clean_line(0, 0)
        self.clean_line(0, self.height - 1)
        self.display_header()
        self.display_footer()

    def clean_line(self, x, y):
        self.stdscr.move(y, x)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()

    def clear_middle_section(self):
        for y in range(1, self.height - 1):
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()

    def package_manager_connection(self, linux_distro_id):
        color_pair = curses.color_pair(4 if self.use_dark_mode else 14)
        color_pair_error = curses.color_pair(2 if self.use_dark_mode else 12)

        while True:
            prompt_checking = "Checking Package Manager Connection"
            x = self.width // 2 - len(prompt_checking) // 2 - 4
            y = self.height // 2 - 2
            self.stdscr.addstr(y, x, prompt_checking)
            self.stdscr.refresh()

            connected = check_linux_package_manager_connection(linux_distro_id)

            if connected:
                self.stdscr.addstr(
                    y, x + len(prompt_checking), " [OK]", color_pair | curses.A_BOLD
                )
                self.stdscr.refresh()
                curses.napms(750)
                return True
            else:
                self.stdscr.addstr(
                    y,
                    x + len(prompt_checking),
                    " [ERROR]",
                    color_pair_error | curses.A_BOLD,
                )
                self.stdscr.refresh()
                prompt = "Retry connection?"
                retry = self.selections(
                    prompt, self.width // 2, self.height // 2, OPTIONS_YES_NO
                )
                if retry == "No":
                    self.clean_line(0, self.height // 2)
                    self.clean_line(0, self.height // 2 + 2)
                    return False
                else:
                    self.clean_line(x, y)

    def print_menu(self, selected_row, relevant_packages, selected_status):
        self.clear_middle_section()

        header_color = curses.color_pair(5 if self.use_dark_mode else 15)
        row_color = curses.color_pair(1 if self.use_dark_mode else 11)
        selected_row_color = (
            curses.color_pair(4 if self.use_dark_mode else 14) | curses.A_REVERSE
        )

        # Draw headers
        table_width = min(self.width - 4, 80)
        table_start_y = 2
        table_start_x = self.width // 2 - table_width // 2

        headers = ["Status", "Package Name"]
        col_width = (table_width - 4) // len(headers)
        for i, header in enumerate(headers):
            x = table_start_x + 7 + i * (col_width - 1)
            self.stdscr.addstr(table_start_y, x, header, header_color)

        # Draw horizontal line under headers
        self.stdscr.hline(
            table_start_y + 1, table_start_x + 1, curses.ACS_HLINE, table_width - 2
        )

        start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES // 2)
        end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

        for idx in range(start_idx, end_idx):
            y = table_start_y + idx - start_idx + 2
            status = "[X] Selected" if selected_status[idx] else "[ ] Unselected"
            package_name = relevant_packages[idx].replace("_", " ")

            color = selected_row_color if idx == selected_row else row_color
            self.stdscr.addstr(y, table_start_x + 2, status.ljust(19), color)
            self.stdscr.addstr(y, table_start_x + 25, package_name.ljust(49), color)

        # Draw arrows
        if start_idx > 0:
            self.stdscr.addstr(
                table_start_y + 2,
                table_start_x + 22,
                "/\\",
                curses.A_BOLD | header_color,
            )
        if end_idx < len(relevant_packages):
            self.stdscr.addstr(
                table_start_y + len(relevant_packages) - 2,
                table_start_x + 22,
                "\\/",
                curses.A_BOLD | header_color,
            )

        self.stdscr.refresh()

    def terminal_size_error(self):
        # Handle terminal size errors
        self.stdscr.clear()

        error_message = (
            "Terminal size is too small. Minimum required is 20 rows and 80 columns."
        )
        x = self.width // 2 - len(error_message) // 2
        y = self.height // 2
        self.stdscr.addstr(y, x, error_message, curses.color_pair(2))
        self.stdscr.refresh()
        curses.napms(3000)
        sys.exit(0)

    def get_user_input_string(self, prompt, y, x):
        color_pair = (
            curses.color_pair(1) if self.use_dark_mode else curses.color_pair(11)
        )
        color_pair_error = (
            curses.color_pair(2) if self.use_dark_mode else curses.color_pair(12)
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
                curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE,
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
                    curses.color_pair(1)
                    if self.use_dark_mode
                    else curses.color_pair(11)
                )
                self.stdscr.refresh()
                self.display_header()
                self.display_footer()
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
                        curses.color_pair(2) | curses.A_BOLD,
                    )
                    self.stdscr.addstr(
                        self.height // 2 + 2,
                        self.width // 2 - len(exit_message) // 2,
                        exit_message,
                        curses.color_pair(2) | curses.A_BOLD,
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
                curses.color_pair(3) | curses.A_BOLD | curses.A_UNDERLINE,
            )
            linux_distribution = get_linux_distribution()
            linux_distro_id = identify_distribution()

            distro_message = "Detected Linux Distro: {}".format(linux_distribution)
            id_message = "Detected Distro ID: {}".format(linux_distro_id)

            self.stdscr.addstr(
                self.height // 2 - 5,
                self.width // 2 - len(distro_message) // 2,
                distro_message,
                curses.color_pair(1),
            )
            self.stdscr.addstr(
                self.height // 2 - 4,
                self.width // 2 - len(id_message) // 2,
                id_message,
                curses.color_pair(1),
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
                        curses.color_pair(1),
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

            self.display_header()
            self.display_footer()

            linux_distribution = self.get_linux_distro()
            output = self.get_output_choice()

            self.clear_middle_section()
            action = self.install_or_remove()

            relevant_packages = self.packages(linux_distribution)
            self.selected_status_array = self.initialize_selected_status(
                len(relevant_packages)
            )

            self.clear_middle_section()
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
                    self.clear_middle_section()
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
                            curses.color_pair(2) | curses.A_BOLD,
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
                        curses.color_pair(5) | curses.A_BOLD,
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
                        self.display_header()
                        self.display_footer()

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
                        curses.color_pair(1)
                        if self.use_dark_mode
                        else curses.color_pair(11)
                    )
                    self.stdscr.refresh()
                    self.display_header()
                    self.display_footer()
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
            self.stdscr.clear()
            self.stdscr.addstr(1, 1, str(e), curses.color_pair(2) | curses.A_BOLD)
            self.stdscr.addstr(2, 1, "[Press any key to exit program]")
            self.stdscr.getch()


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
            curses.color_pair(2) | curses.A_BOLD,
        )
        stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 3, "Bye 👋")
        stdscr.refresh()
        curses.napms(1500)
        curses.endwin()
        sys.exit(0)
