import curses
from packages.packages import packages_data
from time import sleep

from functions.__check_repository_connection__ import check_linux_package_manager_connection
from functions.__get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]
MAX_DISPLAYED_PACKAGES = 5  # Maximum number of packages to display at a time
selected_status_array = []

known_distros = {
    "arch": ["arch"],
    "debian": ["debian"],
    "fedora": ["fedora"],
    "ubuntu": ["ubuntu"],
}

def clean_line(stdscr, x, y):
    stdscr.move(y, x)
    stdscr.clrtoeol()
    stdscr.refresh()


def terminal_size_error(stdscr):
    stdscr.clear()
    stdscr.addstr(
        curses.LINES // 2,
        curses.COLS // 2 - 32,
        "Error: Terminal size is too small. Please resize and try again.",
    )
    stdscr.refresh()
    curses.delay_output(3000)
    exit(1)

def info_messages(stdscr, move_keys, select_keys):
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    height, width = stdscr.getmaxyx()
    # Add the error message with the new color pair
    stdscr.addstr(
        1,
        1,
        "[Press Ctrl + C to exit program]",
        curses.color_pair(2) | curses.A_BOLD,
    )

    stdscr.addstr(
        height - 2,
        width // 2 - 28,
        f"Use {move_keys} arrow keys the move. Select with {select_keys} key.",
    )


def get_user_input_string(stdscr, prompt, y, x):
    curses.echo()
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    while True:
        try:
            input_str = stdscr.getstr().decode("utf-8")
            return input_str
        except curses.error as e:
            if e.code == curses.ERR:
                # End of file (Ctrl+D), handle accordingly or break the loop
                stdscr.addstr(y + 1, x + 1, "End of input. Exiting...")
                stdscr.refresh()
                curses.delay_output(2000)
                exit(0)
            else:
                stdscr.addstr(y + 1, x + 1, "Please give valid input : ")
                stdscr.refresh()


def packages(linux_distro):
    if linux_distro in packages_data:
        package_list = packages_data[linux_distro]
        relevant_packages = []

        for package in package_list:
            relevant_packages.append(package.get("name", ""))
        return relevant_packages
    else:
        return []


def initialize_selected_status(length):
    return [False] * length


def print_menu(stdscr, selected_row, relevant_packages, selected_status):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    info_messages(stdscr, "Up/Down", "Tab")

    start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES + 1)
    end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

    for idx in range(start_idx, end_idx):
        status = relevant_packages[idx].replace("_", " ")
        x = width // 2 - 12
        y = height // 2 - MAX_DISPLAYED_PACKAGES // 2 + idx - start_idx

        if idx == selected_row:
            stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            stdscr.addstr(y, x, status, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            stdscr.addstr(y, x, status)

    # Display scrollbar or arrow if there are more packages
    if start_idx > 0:
        stdscr.addstr(
            height // 2 - MAX_DISPLAYED_PACKAGES // 2 - 2, width // 2 - 6, "---- ^ ----"
        )
    if end_idx < len(relevant_packages):
        stdscr.addstr(
            height // 2 + MAX_DISPLAYED_PACKAGES // 2 + 1, width // 2 - 6, "---- v ----"
        )

    stdscr.refresh()


def selections(stdscr, prompt, x, y, options):
    selected_option = 0
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

    height, width = stdscr.getmaxyx()

    info_messages(stdscr, "Left/Right", "Enter")

    while True:
        stdscr.addstr(
            y, x, prompt, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE
        )

        # Display options side by side
        for i, option in enumerate(options):
            width = x + 16 * i
            height = y + 2
            if i == selected_option:
                stdscr.addstr(height, width, "[" + option + "]", curses.A_REVERSE)
            else:
                stdscr.addstr(height, width, "[" + option + "]")

        stdscr.refresh()

        # Wait for user input
        key = stdscr.getch()

        if key == curses.KEY_LEFT:
            selected_option = (selected_option - 1) % len(options)
        elif key == curses.KEY_RIGHT:
            selected_option = (selected_option + 1) % len(options)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return options[selected_option]


def get_hide_output_choice(stdscr):
    try:
        x = curses.COLS // 2 - 20
        y = curses.LINES // 2 + 3
        prompt = "Do you want to hide package manager output?"
        selection = selections(
            stdscr,
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
        terminal_size_error(stdscr)


def install_or_remove(stdscr):
    try:
        stdscr.clear()
        prompt = "Please select the action:"
        x = curses.COLS // 2 - 13
        y = curses.LINES // 2 - 2
        return selections(stdscr, prompt, x, y, OPTIONS_INSTALL_REMOVE)
    except curses.error:
        terminal_size_error(stdscr)


def get_linux_distro(stdscr):

    try:
        stdscr.addstr(
            curses.LINES // 2 - 5, curses.COLS // 2 - 11, "Getting Linux Distro:"
        )
        linux_distribution = get_linux_distribution()
        linux_distro_id = identify_distribution()

        stdscr.addstr(
            curses.LINES // 2 - 4,
            curses.COLS // 2 - 11,
            "Linux Distro: {}".format(linux_distribution),
        )
        stdscr.addstr(
            curses.LINES // 2 - 3,
            curses.COLS // 2 - 11,
            "Distro ID: {}".format(linux_distro_id),
        )

        prompt = "Is that true?"
        x = curses.COLS // 2 - 11
        y = curses.LINES // 2 - 1
        selected_option = selections(stdscr, prompt, x, y, OPTIONS_YES_NO)

        warning_line = (
            curses.LINES // 2 - 2
        )  # Line where the warning message is displayed

        if selected_option == "Yes":
            return identify_distribution()

        elif selected_option == "No":
            while True:
                linux_distribution = get_user_input_string(
                    stdscr,
                    "Please enter the distro: ",
                    curses.LINES // 2 + 3,
                    curses.COLS // 2 - 11,
                )
                linux_distribution_lower = linux_distribution.lower()

                clean_line(stdscr, curses.COLS // 2 - 11, curses.LINES // 2 - 3)

                stdscr.addstr(
                    curses.LINES // 2 - 3,
                    curses.COLS // 2 - 11,
                    "Entered Linux Distro: {}".format(linux_distribution),
                )

                for distro, keywords in known_distros.items():
                    if any(keyword in linux_distribution_lower for keyword in keywords):
                        clean_line(stdscr, curses.COLS // 2 - 11, warning_line)
                        return distro
                    elif not any(
                        keyword in linux_distribution_lower for keyword in keywords
                    ):
                        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
                        
                        clean_line(stdscr, curses.COLS // 2 - 11, warning_line)

                        # Add the error message with the new color pair
                        stdscr.addstr(
                            warning_line,
                            curses.COLS // 2 - 11,
                            "{} distro not found. Please try again.".format(
                                linux_distribution
                            ),
                            curses.color_pair(2) | curses.A_BOLD,
                        )
                        clean_line(stdscr, curses.COLS // 2 - 11, curses.LINES // 2 + 3)
    except curses.error:
        terminal_size_error(stdscr)


def main(stdscr):
    try:

        curses.curs_set(0)
        linux_distribution = get_linux_distro(stdscr)
        hide_output = get_hide_output_choice(stdscr)
        action = install_or_remove(stdscr)

        relevant_packages = packages(linux_distribution)
        selected_status_array = initialize_selected_status(len(relevant_packages))

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        current_row = 0
        print_menu(stdscr, current_row, relevant_packages, selected_status_array)

        while True:
            key = stdscr.getch()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(relevant_packages)

            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % len(relevant_packages)

            elif key == 9:  # TAB key
                selected_status_array[current_row] = not selected_status_array[
                    current_row
                ]

            elif key == 10:  # Enter key
                stdscr.clear()
                selected_entities = [
                    status
                    for idx, status in enumerate(relevant_packages)
                    if selected_status_array[idx]
                ]

                if not selected_entities:
                    stdscr.addstr(1, curses.COLS // 2 - 12, "Please Select Packages!")
                    stdscr.addstr(3, curses.COLS // 2 - 12, "[Press any arrow key.]", curses.A_REVERSE)
                    continue

                stdscr.addstr(3, curses.COLS // 2 - 12, "Selected applications :")

                for idx, entity in enumerate(selected_entities):
                    stdscr.addstr(4 + idx, curses.COLS // 2 - 12, entity)

                x = curses.COLS // 2 - 12
                y = len(selected_entities) + 5
                prompt = "Do you want to continue?"
                selection = selections(
                    stdscr,
                    prompt,
                    x,
                    y,
                    OPTIONS_YES_NO,
                )

                if selection == "Yes":
                    curses.reset_shell_mode()
                    stdscr.clear()
                    stdscr.refresh()

                    if action == 'install':
                        linux_distro_id = identify_distribution()
                        check_linux_package_manager_connection(linux_distro_id)
                        
                    for idx, entity in enumerate(selected_entities):
                        stdscr.clear()
                        stdscr.refresh()

                        if entity in selected_entities:

                            stdscr.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                f"{entity} {action}ing\n",
                            )
                            get_linux_package_manager(
                                linux_distribution, entity, hide_output, action
                            )
                            sleep(1)

                    curses.reset_prog_mode()
                    stdscr.clear()
                    stdscr.refresh()
                    stdscr.addstr(
                        curses.LINES // 2,
                        curses.COLS // 2 - 21,
                        "The selected options have been implemented!",
                    )
                    stdscr.addstr(
                        curses.LINES // 2 + 1,
                        curses.COLS // 2 - 37,
                        "Reboot for the installed Apps to appear in the App menu and work properly!",
                    )
                    stdscr.getch()
                    break

            print_menu(stdscr, current_row, relevant_packages, selected_status_array)
    except KeyboardInterrupt:
        stdscr.clear()
        stdscr.addstr(
        curses.LINES // 2,
        curses.COLS // 2 - 14,
        "Ctrl + C pressed. Exiting...",
        )
        stdscr.addstr(
            curses.LINES // 2 + 2,
            curses.COLS // 2 - 3,
            "Bye 👋",
        )
        stdscr.refresh()
        curses.delay_output(1500)
        exit(1)
       
    except curses.error:
        terminal_size_error(stdscr)

def start_terminal_gui():
    curses.wrapper(main)
