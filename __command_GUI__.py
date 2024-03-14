import curses
import json
import os
from time import sleep

from __get_os_package_manager__ import (
    get_linux_distribution,
    get_linux_package_manager,
    identify_distribution,
)

OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]
MAX_WRONG_ATTEMPTS = 3
MAX_DISPLAYED_PACKAGES = 5  # Maximum number of packages to display at a time
selected_status_array = []

known_distros = {
    "arch": ["arch"],
    "debian": ["debian"],
    "fedora": ["fedora"],
    "ubuntu": ["ubuntu"],
}


def terminal_size_error(window):
    window.clear()
    window.addstr(
        curses.LINES // 2,
        curses.COLS // 2 - 32,
        "Error: Terminal size is too small. Please resize and try again.",
    )
    window.refresh()
    curses.delay_output(3000)
    exit(1)


def get_user_input_string(window, prompt, y, x):
    curses.echo()
    window.addstr(y, x, prompt)
    window.refresh()
    while True:
        try:
            input_str = window.getstr().decode("utf-8")
            return input_str
        except curses.error as e:
            if e.code == curses.ERR:
                # End of file (Ctrl+D), handle accordingly or break the loop
                window.addstr(y + 1, x + 1, "End of input. Exiting...")
                window.refresh()
                curses.delay_output(2000)
                exit(0)
            else:
                window.addstr(y + 1, x + 1, "Please give valid input : ")
                window.refresh()




def packages(linux_distro):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_directory, "packages.json")

    with open(json_file_path, "r") as json_file:
        instructions_data = json.load(json_file)

    if linux_distro in instructions_data:
        package_list = instructions_data[linux_distro]
        relevant_packages = []

        for idx, package in enumerate(package_list):
            relevant_packages.append(package.get("name", ""))
        return relevant_packages

    else:
        return []


def initialize_selected_status(length):
    return [False] * length


def print_menu(window, selected_row, relevant_packages, selected_status):
    window.clear()
    height, width = window.getmaxyx()

    start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES + 1)
    end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

    for idx in range(start_idx, end_idx):
        status = relevant_packages[idx].replace("_", " ")
        x = width // 2 - 20
        y = height // 2 - MAX_DISPLAYED_PACKAGES // 2 + idx - start_idx

        if idx == selected_row:
            window.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            window.addstr(y, x, status, curses.A_REVERSE)
        else:
            window.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            window.addstr(y, x, status)

    # Display scrollbar or arrow if there are more packages
    if start_idx > 0:
        window.addstr(
            height // 2 - MAX_DISPLAYED_PACKAGES // 2 - 1, width // 2 - 6, "---- ^ ----"
        )
    if end_idx < len(relevant_packages):
        window.addstr(
            height // 2 + MAX_DISPLAYED_PACKAGES // 2 + 1, width // 2 - 6, "---- v ----"
        )

    window.refresh()


def selections(window, prompt, x, y, options):
    selected_option = 0
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

    while True:
        window.addstr(y, x, prompt, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE)

        # Display options side by side
        for i, option in enumerate(options):
            width = x + 16 * i
            height = y + 2
            if i == selected_option:
                window.addstr(height, width, '[' + option + ']', curses.A_REVERSE)
            else:
                window.addstr(height, width, '[' + option + ']')

        window.refresh()

        # Wait for user input
        key = window.getch()

        if key == curses.KEY_LEFT:
            selected_option = (selected_option - 1) % len(options)
        elif key == curses.KEY_RIGHT:
            selected_option = (selected_option + 1) % len(options)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return options[selected_option]
        
def get_hide_output_choice(window):
    x = curses.COLS // 2 - 20
    y = curses.LINES // 2 + 3
    prompt = "Do you want to hide package manager output?"
    selection = selections(
        window,
        prompt,
        x,
        y,
        OPTIONS_YES_NO,
    )

    if selection == "Yes":
        return True
    elif selection == "No":
        return False


def install_or_remove(window):
    window.clear()
    prompt = "Please select the action:"
    x = curses.COLS // 2 - 13
    y = curses.LINES // 2 - 2
    return selections(window, prompt, x, y, OPTIONS_INSTALL_REMOVE)

def get_linux_distro(window):

    window.addstr(
        curses.LINES // 2 - 5, curses.COLS // 2 - 20, "Getting Linux Distro:"
    )
    linux_distribution = get_linux_distribution()
    linux_distro_id = identify_distribution()

    window.addstr(
        curses.LINES // 2 - 4,
        curses.COLS // 2 - 20,
        "Linux Distro: {}".format(linux_distribution),
    )
    window.addstr(
        curses.LINES // 2 - 3,
        curses.COLS // 2 - 20,
        "Distro ID: {}".format(linux_distro_id),
    )

    prompt = "Is that true?"
    x = curses.COLS // 2 - 20
    y = curses.LINES // 2 - 1
    selected_option = selections(window, prompt, x, y, OPTIONS_YES_NO)

    warning_line = (
            curses.LINES // 2 - 2
        )  # Line where the warning message is displayed

    if selected_option == "Yes":
        return identify_distribution()
    elif selected_option == "No":
        while True:
            linux_distribution = get_user_input_string(
                window,
                "Please enter the distro: ",
                curses.LINES // 2 + 3,
                curses.COLS // 2 - 20,
            )
            linux_distribution_lower = linux_distribution.lower()

            window = curses.initscr()
            window.clrtoeol()
            window.refresh()
            window.addstr(
                curses.LINES // 2 - 3,
                curses.COLS // 2 - 20,
                "Entered Linux Distro: {}".format(linux_distribution),
            )

            for distro, keywords in known_distros.items():
                if any(keyword in linux_distribution_lower for keyword in keywords):
                    # Clear the warning message line when the correct key is entered
                    window.move(warning_line, 0)
                    window.clrtoeol()
                    return distro
                elif not any(keyword in linux_distribution_lower for keyword in keywords):
                    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

                    # Add the error message with the new color pair
                    window.addstr(
                        warning_line,
                        curses.COLS // 2 - 20,
                        "{} distro not found. Please try again.".format(linux_distribution),
                        curses.color_pair(2) | curses.A_BOLD
                    )


def main(window):
    try:

        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        window.bkgd(' ', curses.color_pair(5))

        curses.curs_set(0)
        linux_distribution = get_linux_distro(window)
        hide_output = get_hide_output_choice(window)
        action = install_or_remove(window)

        relevant_packages = packages(linux_distribution)
        selected_status_array = initialize_selected_status(len(relevant_packages))

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        current_row = 0
        print_menu(window, current_row, relevant_packages, selected_status_array)

        while True:
            key = window.getch()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(relevant_packages)

            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % len(relevant_packages)

            elif key == 9:  # TAB key
                selected_status_array[current_row] = not selected_status_array[
                    current_row
                ]

            elif key == 10:  # Enter key
                window.clear()
                selected_entities = [
                    status
                    for idx, status in enumerate(relevant_packages)
                    if selected_status_array[idx]
                ]
                window.addstr(1, curses.COLS // 2 - 21, "Selected applications :")

                for idx, entity in enumerate(selected_entities):
                    window.addstr(2 + idx, curses.COLS // 2 - 21, entity)

                x = curses.COLS // 2 - 21
                y = len(selected_entities) + 3
                prompt = "Do you want to continue?"
                selection = selections(
                    window,
                    prompt,
                    x,
                    y,
                    OPTIONS_YES_NO,
                )

                if selection == "Yes":
                    for idx, entity in enumerate(selected_entities):
                        window.clear()
                        window.refresh()
                        if entity in selected_entities:
                            curses.reset_shell_mode()
                            window.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                "{} installing\n".format(entity),
                            )
                            get_linux_package_manager(
                                linux_distribution, entity, hide_output, action
                            )
                            sleep(3)
                    curses.reset_prog_mode()
                    window.clear()
                    window.refresh()
                    window.addstr(
                        curses.LINES // 2,
                        curses.COLS // 2 - 21,
                        "The selected options have been implemented!",
                    )
                    window.addstr(
                        curses.LINES // 2 + 1,
                        curses.COLS // 2 - 37,
                        "Reboot for the installed Apps to appear in the App menu and work properly!",
                    )
                    window.getch()
                    break

            print_menu(window, current_row, relevant_packages, selected_status_array)
    except KeyboardInterrupt:
        window.clear()
        window.addstr(
            curses.LINES // 2,
            curses.COLS // 2 - 14,
            "Ctrl + C pressed. Exiting...",
        )
        window.addstr(
            curses.LINES // 2 + 2,
            curses.COLS // 2 - 3,
            "Bye 👋",
        )
        window.refresh()
        curses.delay_output(1500)
        exit(1)
    except curses.error:
         terminal_size_error(window)


curses.wrapper(main)
