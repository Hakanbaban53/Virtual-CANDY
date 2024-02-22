import curses
import json
import os
from __get_os_package_manager__ import (
    get_linux_distribution,
    identify_distribution,
    get_linux_package_manager,
)

MAX_WRONG_ATTEMPTS = 3
max_displayed_packages = 3  # Maximum number of packages to display at a time
selected_status_array = []

known_distros = {
    "arch": ["arch"],
    "debian": ["debian"],
    "fedora": ["fedora"],
    "ubuntu": ["ubuntu"],
}


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

    start_idx = max(0, selected_row - max_displayed_packages + 1)
    end_idx = min(len(relevant_packages), start_idx + max_displayed_packages)

    for idx in range(start_idx, end_idx):
        status = relevant_packages[idx]
        x = width // 2 - len(status) // 2
        y = height // 2 - max_displayed_packages // 2 + idx - start_idx

        if idx == selected_row:
            window.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            window.addstr(y, x, status, curses.A_REVERSE)
        else:
            window.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            window.addstr(y, x, status)

    # Display scrollbar or arrow if there are more packages
    if start_idx > 0:
        window.addstr(
            height // 2 - max_displayed_packages // 2 - 1, width // 2 - 6, "---- ^ ----"
        )
    if end_idx < len(relevant_packages):
        window.addstr(
            height // 2 + max_displayed_packages // 2 + 1, width // 2 - 6, "---- v ----"
        )

    window.refresh()


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


def get_user_input_char(window, prompt, y, x):
    curses.echo()
    window.addstr(y, x, prompt)
    window.refresh()
    while True:
        try:
            input_char = window.getch()
            return input_char
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


def get_hide_output_choice(window):
    wrong_attempts = 0

    while True:
        confirmation_key = get_user_input_char(
            window,
            "Do you want to hide package manager output? [Y/n]: ",
            curses.LINES // 2 + 5,
            curses.COLS // 2 - 20,
        )

        if confirmation_key in [89, 121, 10, 13]:  # 'Y', 'y', Enter, Carriage Return
            return True
        elif confirmation_key in [78, 110]:  # 'N', 'n'
            return False
        else:
            wrong_attempts += 1

            if wrong_attempts >= MAX_WRONG_ATTEMPTS:
                window.clear()
                window.addstr(
                    curses.LINES // 2 + 1,
                    curses.COLS // 2 - 20,
                    "Too many wrong attempts. Exiting in 3 seconds...",
                )
                window.refresh()
                curses.delay_output(3000)
                exit(1)
            else:
                window.addstr(
                    curses.LINES // 2 + 6,
                    curses.COLS // 2 - 20,
                    "Unknown key! Try again (Attempts left: {})".format(
                        MAX_WRONG_ATTEMPTS - wrong_attempts
                    ),
                )

        window.refresh()


def spinning_icon(window, entity):
    icons = ["-", "\\", "|", "/"]
    i = 0
    while True:
        window.addstr(0, 0, f"Installing {entity}... {icons[i]}", curses.A_BOLD)
        window.refresh()
        i = (i + 1) % len(icons)
        curses.napms(200)  # Sleep for 200 milliseconds


def get_linux_distro(window):

    try:
        window.clear()
        wrong_attempts = 0
        warning_line = (
            curses.LINES // 2 + 3
        )  # Line where the warning message is displayed

        window.addstr(
            curses.LINES // 2 - 2, curses.COLS // 2 - 20, "Getting Linux Distro:"
        )
        linux_distribution = get_linux_distribution()
        linux_distro_id = identify_distribution()

        window.addstr(
            curses.LINES // 2 - 1,
            curses.COLS // 2 - 20,
            "Linux Distro: {}".format(linux_distribution),
        )
        window.addstr(
            curses.LINES // 2,
            curses.COLS // 2 - 20,
            "Distro ID: {}".format(linux_distro_id),
        )

        while True:
            confirmation_key = get_user_input_char(
                window,
                "Is it correct? [Y/n]: ",
                curses.LINES // 2 + 1,
                curses.COLS // 2 - 20,
            )

            if confirmation_key in [
                89,
                121,
                10,
                13,
            ]:  # 'Y', 'y', Enter, Carriage Return
                window.move(warning_line, 0)
                window.clrtoeol()
                return linux_distro_id

            elif confirmation_key in [78, 110]:  # 'N', 'n'
                while True:

                    linux_distribution = get_user_input_string(
                        window,
                        "Please enter the distro: ",
                        curses.LINES // 2 + 2,
                        curses.COLS // 2 - 20,
                    )
                    linux_distribution_lower = linux_distribution.lower()

                    window.move(curses.LINES // 2 + 4, curses.COLS // 2 - 20)
                    window.clrtoeol()

                    window.addstr(
                        curses.LINES // 2 + 4,
                        curses.COLS // 2 - 20,
                        "Entered Linux Distro: {}".format(linux_distribution),
                    )

                    for distro, keywords in known_distros.items():
                        if any(
                            keyword in linux_distribution_lower for keyword in keywords
                        ):
                            # Clear the warning message line when the correct key is entered
                            window.move(warning_line, 0)
                            window.clrtoeol()
                            return distro

                    window.addstr(
                        warning_line,
                        curses.COLS // 2 - 20,
                        "Unknown distro! Try again...(Attempts left: {})".format(
                            MAX_WRONG_ATTEMPTS - wrong_attempts
                        ),
                    )
                    wrong_attempts += 1

                    if wrong_attempts >= MAX_WRONG_ATTEMPTS:
                        window.clear()
                        window.addstr(
                            curses.LINES // 2 + 9,
                            curses.COLS // 2 - 20,
                            "Too many wrong attempts. Exiting in 3 seconds...",
                        )
                        window.refresh()
                        curses.delay_output(3000)
                        exit(1)

                    window.refresh()

            else:
                wrong_attempts += 1

                if wrong_attempts >= MAX_WRONG_ATTEMPTS:
                    window.clear()
                    window.addstr(
                        curses.LINES // 2 + 1,
                        curses.COLS // 2 - 20,
                        "Too many wrong attempts. Exiting in 3 seconds...",
                    )
                    window.refresh()
                    curses.delay_output(3000)
                    exit(1)
                else:
                    # Clear the line before displaying the warning about the unknown key and attempt count
                    window.move(curses.LINES // 2 + 6, curses.COLS // 2 - 20)
                    window.clrtoeol()

                    # Display warning about the unknown key and attempt count
                    window.addstr(
                        warning_line,
                        curses.COLS // 2 - 20,
                        "Unknown command! Try again... (Attempts left: {})".format(
                            MAX_WRONG_ATTEMPTS - wrong_attempts
                        ),
                    )
                    window.refresh()

    except curses.error:
        window.clear()
        window.addstr(
            curses.LINES // 2,
            curses.COLS // 2 - 20,
            "Error: Terminal size is too small. Please resize and try again.",
        )
        window.refresh()
        curses.delay_output(3000)
        exit(1)


def main(window):
    try:
        linux_distribution = get_linux_distro(window)
        hide_output = get_hide_output_choice(window)

        relevant_packages = packages(linux_distribution)
        selected_status_array = initialize_selected_status(len(relevant_packages))

        curses.curs_set(0)
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
                window.addstr(1, 3, "Selected applications :")
                window.addstr(0, 0, "{}".format(hide_output))

                for idx, entity in enumerate(selected_entities):
                    window.addstr(2 + idx, 3, entity)

                window.addstr(
                    len(selected_entities) + 3, 3, "Do you want to continue[Y/n]? \n"
                )
                window.refresh()
                confirmation_key = window.getch()
                if confirmation_key in [
                    89,
                    121,
                    10,
                    13,
                ]:  # 'Y', 'y', Enter, Carriage Return
                    for idx, entity in enumerate(selected_entities):
                        window.clear()
                        window.refresh()
                        if entity in selected_entities:
                            if hide_output:
                                spinning_icon(window, entity)
                                get_linux_package_manager(
                                    linux_distribution, entity, hide_output
                                )
                            else:
                                window.addstr(0, 0, "{} installing...\n".format(entity),)
                                get_linux_package_manager(
                                    linux_distribution, entity, hide_output
                                )
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

    finally:
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


curses.wrapper(main)
