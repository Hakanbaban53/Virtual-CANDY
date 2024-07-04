import curses
from time import sleep
from functools import partial
from functions.__check_repository_connection__ import check_linux_package_manager_connection
from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)
from functions.__get_packages_data__ import PackagesJSONHandler

# Constants
OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]
MAX_DISPLAYED_PACKAGES = 15

class PackageManagerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.selected_status_array = []
        self.use_dark_mode = True  # Default to dark mode
        self.known_distros = {
            "arch": ["arch"],
            "debian": ["debian"],
            "fedora": ["fedora"],
            "ubuntu": ["ubuntu"],
        }
        self.init_colors()

    def init_colors(self):
        # Initialize color pairs based on mode
        dark_mode = self.use_dark_mode
        color_pair = partial(curses.color_pair, 1 if dark_mode else 11)
        
        # Dark mode color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Default text color
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Error messages
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Header
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Selected row
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Table headers

        # Light mode color pairs
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Default text color
        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_WHITE)    # Error messages
        curses.init_pair(13, curses.COLOR_CYAN, curses.COLOR_WHITE)   # Header
        curses.init_pair(14, curses.COLOR_GREEN, curses.COLOR_WHITE)  # Selected row
        curses.init_pair(15, curses.COLOR_YELLOW, curses.COLOR_WHITE) # Table headers


    def display_header(self):
        # Display header
        color_pair = curses.color_pair(3) if self.use_dark_mode else curses.color_pair(13)
        self.stdscr.addstr(0, self.width // 2 - len("VCANDY") // 2, "VCANDY", color_pair | curses.A_BOLD | curses.A_UNDERLINE)

    def display_footer(self):
        # Display footer with information messages
        color_pair = curses.color_pair(1) if self.use_dark_mode else curses.color_pair(11)
        color_pair_error = curses.color_pair(2) if self.use_dark_mode else curses.color_pair(12)

        self.stdscr.addstr(curses.LINES - 1, 1, "[Press Ctrl + C to exit program]", color_pair_error | curses.A_BOLD)
        self.stdscr.addstr(curses.LINES - 1, curses.COLS // 2 - 28, "Use Up/Down arrow keys to move. Select with Tab key.", color_pair)

    def print_menu(self, selected_row, relevant_packages, selected_status):
        # Print menu with package information
        self.clear_middle_section()

        header_color = curses.color_pair(5) if self.use_dark_mode else curses.color_pair(15)
        row_color = curses.color_pair(1) if self.use_dark_mode else curses.color_pair(11)
        selected_row_color = curses.color_pair(4) | curses.A_REVERSE if self.use_dark_mode else curses.color_pair(14) | curses.A_REVERSE
        background_color = curses.COLOR_BLACK if self.use_dark_mode else curses.COLOR_WHITE

        # Draw headers
        table_width = min(self.width - 4, 80)
        table_start_y = 2
        table_start_x = self.width // 2 - table_width // 2

        headers = ["Status", "Package Name"]
        col_width = (table_width - 4) // len(headers)
        for i, header in enumerate(headers):
            x = table_start_x + 2 + i * (col_width + 1)
            self.stdscr.addstr(table_start_y, x, header.center(col_width), header_color)

        # Draw horizontal line under headers
        self.stdscr.hline(table_start_y + 1, table_start_x + 1, curses.ACS_HLINE, table_width - 2)

        # Display packages
        start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES + 1)
        end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

        for idx in range(start_idx, end_idx):
            y = table_start_y + idx - start_idx + 2
            status = "[X]" if selected_status[idx] else "[ ]"
            package_name = relevant_packages[idx].replace("_", " ")

            color = selected_row_color if idx == selected_row else row_color
            self.stdscr.addstr(y, table_start_x + 2, status, color)
            self.stdscr.addstr(y, table_start_x + 8, package_name, color)

        self.stdscr.refresh()

    def clear_middle_section(self):
        # Clear middle section of the screen
        start_y = 1
        end_y = self.height - 1
        for y in range(start_y, end_y):
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()

    def get_user_input_string(self, prompt, y, x):
        # Get user input string
        curses.echo()
        self.stdscr.addstr(y, x, prompt)
        self.stdscr.refresh()
        while True:
            try:
                input_str = self.stdscr.getstr().decode("utf-8")
                return input_str.strip()
            except curses.error:
                self.stdscr.addstr(y + 1, x + 1, "Error: Invalid input.")
                self.stdscr.refresh()

    def selections(self, prompt, x, y, options):
        # Handle user selections
        selected_option = 0

        while True:
            self.stdscr.addstr(y, x, prompt, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE)

            for i, option in enumerate(options):
                width = x + 16 * i
                height = y + 2
                if i == selected_option:
                    self.stdscr.addstr(height, width, "[" + option + "]", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(height, width, "[" + option + "]")

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_LEFT:
                selected_option = (selected_option - 1) % len(options)
            elif key == curses.KEY_RIGHT:
                selected_option = (selected_option + 1) % len(options)
            elif key in [curses.KEY_ENTER, 10, 13]:
                return options[selected_option]

    def get_hide_output_choice(self):
        # Prompt user for hide output choice
        try:
            prompt = "Do you want to hide package manager output?"
            x = curses.COLS // 2 - len(prompt) // 2
            y = curses.LINES // 2 + 3
            selection = self.selections(prompt, x, y, OPTIONS_YES_NO)
            return selection == "Yes"

        except curses.error:
            self.terminal_size_error()

    def install_or_remove(self):
        # Prompt user for installation or removal action
        try:
            prompt = "Please select the action:"
            x = curses.COLS // 2 - len(prompt) // 2
            y = curses.LINES // 2 - 2
            return self.selections(prompt, x, y, OPTIONS_INSTALL_REMOVE)

        except curses.error:
            self.terminal_size_error()

    def get_linux_distro(self):
        # Retrieve Linux distribution from user input or automatic detection
        try:
            self.stdscr.addstr(curses.LINES // 2 - 5, curses.COLS // 2 - 14, "Getting Linux Distro:")
            linux_distribution = get_linux_distribution()
            linux_distro_id = identify_distribution()

            self.stdscr.addstr(curses.LINES // 2 - 4, curses.COLS // 2 - 14, "Linux Distro: {}".format(linux_distribution))
            self.stdscr.addstr(curses.LINES // 2 - 3, curses.COLS // 2 - 14, "Distro ID: {}".format(linux_distro_id))

            prompt = "Is that true?"
            x = curses.COLS // 2 - 14
            y = curses.LINES // 2 - 1
            selected_option = self.selections(prompt, x, y, OPTIONS_YES_NO)

            if selected_option == "Yes":
                return linux_distro_id

            elif selected_option == "No":
                while True:
                    linux_distribution = self.get_user_input_string("Please enter the distro: ", curses.LINES // 2 + 3, curses.COLS // 2 - 14)
                    linux_distribution_lower = linux_distribution.lower()

                    self.clean_line(curses.COLS // 2 - 14, curses.LINES // 2 - 3)
                    self.stdscr.addstr(curses.LINES // 2 - 3, curses.COLS // 2 - 14, "Entered Linux Distro: {}".format(linux_distribution))

                    for distro, keywords in self.known_distros.items():
                        if linux_distribution_lower in keywords:
                            return distro

                    warning_line = curses.LINES // 2 - 2
                    self.clean_line(curses.COLS // 2 - 14, warning_line)
                    self.stdscr.addstr(warning_line, curses.COLS // 2 - 14, "{} distro not found. Please try again.".format(linux_distribution), curses.color_pair(2) | curses.A_BOLD)
                    self.clean_line(curses.COLS // 2 - 14, curses.LINES // 2 + 3)

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

    def terminal_size_error(self):
        # Handle terminal size error
        self.clear_middle_section()
        self.stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 32, "Error: Terminal size is too small. Please resize and try again.")
        self.stdscr.refresh()
        curses.napms(3000)
        exit(1)

    def main(self):
        # Main application logic
        try:
            curses.curs_set(0)
            if curses.LINES < 20 or curses.COLS < 80:
                self.terminal_size_error()

            self.display_header()
            self.display_footer()

            linux_distribution = self.get_linux_distro()
            hide_output = self.get_hide_output_choice()

            self.clear_middle_section()
            action = self.install_or_remove()

            relevant_packages = self.packages(linux_distribution)
            self.selected_status_array = self.initialize_selected_status(len(relevant_packages))

            self.print_menu(0, relevant_packages, self.selected_status_array)
            current_row = 0

            while True:
                key = self.stdscr.getch()

                if key == curses.KEY_DOWN:
                    current_row = (current_row + 1) % len(relevant_packages)

                elif key == curses.KEY_UP:
                    current_row = (current_row - 1) % len(relevant_packages)

                elif key == 9:  # TAB key
                    self.selected_status_array[current_row] = not self.selected_status_array[current_row]

                elif key == 10:  # Enter key
                    self.clear_middle_section()
                    selected_entities = [status for idx, status in enumerate(relevant_packages) if self.selected_status_array[idx]]

                    if not selected_entities:
                        self.stdscr.addstr(1, curses.COLS // 2 - 12, "Please Select Packages!")
                        self.stdscr.addstr(3, curses.COLS // 2 - 12, "[Press any arrow key.]", curses.A_REVERSE)
                        continue

                    self.stdscr.addstr(3, curses.COLS // 2 - 12, "Selected applications :")

                    for idx, entity in enumerate(selected_entities):
                        self.stdscr.addstr(4 + idx, curses.COLS // 2 - 12, entity)

                    x = curses.COLS // 2 - 12
                    y = len(selected_entities) + 5
                    prompt = "Do you want to continue?"
                    selection = self.selections(prompt, x, y, OPTIONS_YES_NO)

                    if selection == "Yes":
                        curses.reset_shell_mode()
                        self.clear_middle_section()

                        # Execute selected actions
                        if action == "install":
                            linux_distro_id = identify_distribution()
                            check_linux_package_manager_connection(linux_distro_id)

                        for idx, entity in enumerate(selected_entities):
                            self.stdscr.addstr(len(selected_entities) + 4 + idx, 3, f"{entity} {action}ing\n")
                            get_linux_package_manager(linux_distribution, entity, hide_output, action)
                            sleep(1)

                        curses.reset_prog_mode()
                        self.clear_middle_section()
                        self.stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 21, "The selected options have been implemented!")
                        self.stdscr.addstr(curses.LINES // 2 + 1, curses.COLS // 2 - 37, "Reboot for the installed Apps to appear in the App menu and work properly!")
                        self.stdscr.getch()
                        break

                elif key == 4:  # Ctrl + D for toggle dark/light mode
                    self.use_dark_mode = not self.use_dark_mode
                    self.stdscr.bkgd(curses.color_pair(1) if self.use_dark_mode else curses.color_pair(11))
                    self.stdscr.refresh()
                    self.display_header()
                    self.display_footer()
                    self.print_menu(current_row, relevant_packages, self.selected_status_array)

                self.print_menu(current_row, relevant_packages, self.selected_status_array)

        except KeyboardInterrupt:
            self.clear_middle_section()
            self.stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 14, "Ctrl + C pressed. Exiting...")
            self.stdscr.addstr(curses.LINES // 2 + 2, curses.COLS // 2 - 3, "Bye 👋")
            self.stdscr.refresh()
            curses.napms(1500)
            exit(1)

        except curses.error:
            self.terminal_size_error()

        except Exception as e:
            self.stdscr.clear()
            self.stdscr.addstr(1, 1, str(e))
            self.stdscr.addstr(2, 1, "[Press any key to exit program]", curses.A_REVERSE)
            self.stdscr.getch()

def start_terminal_ui():
    curses.wrapper(lambda stdscr: PackageManagerApp(stdscr).main())

