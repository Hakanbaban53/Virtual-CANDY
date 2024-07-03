import curses
from time import sleep

from functions.__check_repository_connection__ import check_linux_package_manager_connection
from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)
from functions.__get_packages_data__ import PackagesJSONHandler

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]
MAX_DISPLAYED_PACKAGES = 5  # Maximum number of packages to display at a time

class PackageManagerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.selected_status_array = []
        self.known_distros = {
            "arch": ["arch"],
            "debian": ["debian"],
            "fedora": ["fedora"],
            "ubuntu": ["ubuntu"],
        }

    def clean_line(self, x, y):
        self.stdscr.move(y, x)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()

    def terminal_size_error(self):
        self.stdscr.clear()
        self.stdscr.addstr(
            curses.LINES // 2,
            curses.COLS // 2 - 32,
            "Error: Terminal size is too small. Please resize and try again.",
        )
        self.stdscr.refresh()
        curses.delay_output(3000)
        exit(1)

    def info_messages(self, move_keys, select_keys):
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(
            1,
            1,
            "[Press Ctrl + C to exit program]",
            curses.color_pair(2) | curses.A_BOLD,
        )

        self.stdscr.addstr(
            height - 2,
            width // 2 - 28,
            f"Use {move_keys} arrow keys to move. Select with {select_keys} key.",
        )

    def get_user_input_string(self, prompt, y, x):
        curses.echo()
        self.stdscr.addstr(y, x, prompt)
        self.stdscr.refresh()
        while True:
            try:
                input_str = self.stdscr.getstr().decode("utf-8")
                return input_str
            except curses.error as e:
                if e.code == curses.ERR:
                    self.stdscr.addstr(y + 1, x + 1, "End of input. Exiting...")
                    self.stdscr.refresh()
                    curses.delay_output(2000)
                    exit(0)
                else:
                    self.stdscr.addstr(y + 1, x + 1, "Please give valid input : ")
                    self.stdscr.refresh()

    def packages(self, linux_distro):
        handler = PackagesJSONHandler()
        instructions_data = handler.load_json_data()

        if linux_distro in instructions_data:
            package_list = instructions_data[linux_distro]
            relevant_packages = [package.get("name", "") for package in package_list]
            return relevant_packages
        else:
            return []

    def initialize_selected_status(self, length):
        return [False] * length

    def print_menu(self, selected_row, relevant_packages, selected_status):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        self.info_messages("Up/Down", "Tab")

        start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES + 1)
        end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

        for idx in range(start_idx, end_idx):
            status = relevant_packages[idx].replace("_", " ")
            x = width // 2 - 12
            y = height // 2 - MAX_DISPLAYED_PACKAGES // 2 + idx - start_idx

            if idx == selected_row:
                self.stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
                self.stdscr.addstr(y, x, status, curses.A_REVERSE)
            else:
                self.stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
                self.stdscr.addstr(y, x, status)

        if start_idx > 0:
            self.stdscr.addstr(
                height // 2 - MAX_DISPLAYED_PACKAGES // 2 - 2, width // 2 - 6, "---- ^ ----"
            )
        if end_idx < len(relevant_packages):
            self.stdscr.addstr(
                height // 2 + MAX_DISPLAYED_PACKAGES // 2 + 1, width // 2 - 6, "---- v ----"
            )

        self.stdscr.refresh()

    def selections(self, prompt, x, y, options):
        selected_option = 0
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        height, width = self.stdscr.getmaxyx()

        self.info_messages("Left/Right", "Enter")

        while True:
            self.stdscr.addstr(
                y, x, prompt, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE
            )

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
        try:
            x = curses.COLS // 2 - 14
            y = curses.LINES // 2 + 3
            prompt = "Do you want to hide package manager output?"
            selection = self.selections(
                prompt,
                x,
                y,
                OPTIONS_YES_NO,
            )

            if selection == "Yes":
                return True
            elif selection == "No":
                return False
        except curses.error:
            self.terminal_size_error()

    def install_or_remove(self):
        try:
            self.stdscr.clear()
            prompt = "Please select the action:"
            x = curses.COLS // 2 - 14
            y = curses.LINES // 2 - 2
            return self.selections(prompt, x, y, OPTIONS_INSTALL_REMOVE)
        except curses.error:
            self.terminal_size_error()

    def get_linux_distro(self):
        try:
            self.stdscr.addstr(
                curses.LINES // 2 - 5, curses.COLS // 2 - 14, "Getting Linux Distro:"
            )
            linux_distribution = get_linux_distribution()
            linux_distro_id = identify_distribution()

            self.stdscr.addstr(
                curses.LINES // 2 - 4,
                curses.COLS // 2 - 14,
                "Linux Distro: {}".format(linux_distribution),
            )
            self.stdscr.addstr(
                curses.LINES // 2 - 3,
                curses.COLS // 2 - 14,
                "Distro ID: {}".format(linux_distro_id),
            )

            prompt = "Is that true?"
            x = curses.COLS // 2 - 14
            y = curses.LINES // 2 - 1
            selected_option = self.selections(prompt, x, y, OPTIONS_YES_NO)

            warning_line = curses.LINES // 2 - 2  # Line where the warning message is displayed

            if selected_option == "Yes":
                return identify_distribution()

            elif selected_option == "No":
                while True:
                    linux_distribution = self.get_user_input_string(
                        "Please enter the distro: ",
                        curses.LINES // 2 + 3,
                        curses.COLS // 2 - 14,
                    )
                    linux_distribution_lower = linux_distribution.lower()

                    self.clean_line(curses.COLS // 2 - 14, curses.LINES // 2 - 3)

                    self.stdscr.addstr(
                        curses.LINES // 2 - 3,
                        curses.COLS // 2 - 14,
                        "Entered Linux Distro: {}".format(linux_distribution),
                    )

                    for distro, keywords in self.known_distros.items():
                        if any(keyword in linux_distribution_lower for keyword in keywords):
                            self.clean_line(curses.COLS // 2 - 14, warning_line)
                            return distro
                        elif not any(
                            keyword in linux_distribution_lower for keyword in keywords
                        ):
                            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

                            self.clean_line(curses.COLS // 2 - 14, warning_line)

                            self.stdscr.addstr(
                                warning_line,
                                curses.COLS // 2 - 14,
                                "{} distro not found. Please try again.".format(
                                    linux_distribution
                                ),
                                curses.color_pair(2) | curses.A_BOLD,
                            )
                            self.clean_line(curses.COLS // 2 - 14, curses.LINES // 2 + 3)
        except curses.error:
            self.terminal_size_error()

    def main(self):
        try:
            curses.curs_set(0)
            linux_distribution = self.get_linux_distro()
            hide_output = self.get_hide_output_choice()
            action = self.install_or_remove()

            relevant_packages = self.packages(linux_distribution)
            self.selected_status_array = self.initialize_selected_status(len(relevant_packages))

            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

            current_row = 0
            self.print_menu(current_row, relevant_packages, self.selected_status_array)

            while True:
                key = self.stdscr.getch()

                if key == curses.KEY_DOWN:
                    current_row = (current_row + 1) % len(relevant_packages)

                elif key == curses.KEY_UP:
                    current_row = (current_row - 1) % len(relevant_packages)

                elif key == 9:  # TAB key
                    self.selected_status_array[current_row] = not self.selected_status_array[current_row]

                elif key == 10:  # Enter key
                    self.stdscr.clear()
                    selected_entities = [
                        status
                        for idx, status in enumerate(relevant_packages)
                        if self.selected_status_array[idx]
                    ]

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
                        self.stdscr.clear()
                        self.stdscr.refresh()

                        if action == 'install':
                            linux_distro_id = identify_distribution()
                            check_linux_package_manager_connection(linux_distro_id)

                        for idx, entity in enumerate(selected_entities):
                            self.stdscr.clear()
                            self.stdscr.refresh()

                            if entity in selected_entities:
                                self.stdscr.addstr(
                                    len(selected_entities) + 4 + idx,
                                    3,
                                    f"{entity} {action}ing\n",
                                )
                                get_linux_package_manager(
                                    linux_distribution, entity, hide_output, action
                                )
                                sleep(1)

                        curses.reset_prog_mode()
                        self.stdscr.clear()
                        self.stdscr.refresh()
                        self.stdscr.addstr(
                            curses.LINES // 2,
                            curses.COLS // 2 - 21,
                            "The selected options have been implemented!",
                        )
                        self.stdscr.addstr(
                            curses.LINES // 2 + 1,
                            curses.COLS // 2 - 37,
                            "Reboot for the installed Apps to appear in the App menu and work properly!",
                        )
                        self.stdscr.getch()
                        break

                self.print_menu(current_row, relevant_packages, self.selected_status_array)

        except KeyboardInterrupt:
            self.stdscr.clear()
            self.stdscr.addstr(
                curses.LINES // 2,
                curses.COLS // 2 - 14,
                "Ctrl + C pressed. Exiting...",
            )
            self.stdscr.addstr(
                curses.LINES // 2 + 2,
                curses.COLS // 2 - 3,
                "Bye 👋",
            )
            self.stdscr.refresh()
            curses.delay_output(1500)
            exit(1)

        except curses.error:
            self.terminal_size_error()

def start_terminal_gui():
    curses.wrapper(lambda stdscr: PackageManagerApp(stdscr).main())
