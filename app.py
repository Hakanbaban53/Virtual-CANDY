import curses
from __get_os_package_manager__ import (
    get_linux_distribution,
    identify_distribution,
    get_linux_package_manager,
)

MAX_WRONG_ATTEMPTS = 3

packages = [
    "Docker & Docker Desktop",
    "Podman & Podman Desktop",
    "Qemu & Virtual Manager",
    "Virtual Box",
    "Package 5",
    "Package 6",
    # Add more packages as needed
]
selected_status = [False] * len(packages)
max_displayed_packages = 3  # Maximum number of packages to display at a time

def print_menu(window, selected_row):
    window.clear()
    height, width = window.getmaxyx()

    start_idx = max(0, selected_row - max_displayed_packages + 1)
    end_idx = min(len(packages), start_idx + max_displayed_packages)

    for idx in range(start_idx, end_idx):
        status = packages[idx]
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
        window.addstr(height // 2 - max_displayed_packages // 2 - 1, width // 2 - 6, '---- 🡅  ----')
    if end_idx < len(packages):
        window.addstr(height // 2 + max_displayed_packages // 2 + 1, width // 2 - 6, '---- 🡇  ----')

    window.refresh()


def get_user_input_string(window, prompt, y, x):
    curses.echo()
    window.addstr(y, x, prompt)
    window.refresh()
    try:
        input_str = window.getstr().decode("utf-8")
    except curses.error:
        input_str = ""  # Handle input errors or interruptions
    curses.noecho()
    return input_str


def get_user_input_char(window, prompt, y, x):
    curses.echo()
    window.addstr(y, x, prompt)
    window.refresh()
    input_char = window.getch()
    return input_char


def get_hide_output_choice(window):
    wrong_attempts = 0

    while True:
        confirmation_key = get_user_input_char(
            window,
            "Do you want to hide package manager output? [Y/n]: ",
            curses.LINES // 2 + 5,
            curses.COLS // 2 - 20,
        )

        if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
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


def spinning_icon(window, pause_event):
    icons = ["-", "\\", "|", "/"]
    i = 0
    while not pause_event.is_set():
        window.addstr(0, 0, f"Installing... {icons[i]}", curses.A_BOLD)
        window.refresh()
        i = (i + 1) % len(icons)
        curses.napms(200)  # Sleep for 200 milliseconds
    window.addstr(0, 0, "Installation paused... ", curses.A_BOLD)
    window.refresh()


    # Inside the get_linux_distro function
def get_linux_distro(window):

    try:    
        window.clear()
        wrong_attempts = 0
        warning_line = curses.LINES // 2 + 3  # Line where the warning message is displayed

        window.addstr(curses.LINES // 2 - 2, curses.COLS // 2 - 20, "Getting Linux Distro:")
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
                "Is it correct? [Y/n]",
                curses.LINES // 2 + 1,
                curses.COLS // 2 - 20,
            )

            if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
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

                    known_distros = {
                        "arch": ["arch", "manjaro"],
                        "debian": ["debian"],
                        "fedora": ["fedora", "nobara"],
                        "ubuntu": ["ubuntu", "linux mint"],
                    }

                    for distro, keywords in known_distros.items():
                        if any(keyword in linux_distribution_lower for keyword in keywords):
                            # Clear the warning message line when the correct key is entered
                            window.move(warning_line, 0)
                            window.clrtoeol()
                            return distro

                    window.addstr(
                        curses.LINES // 2 + 8,
                        curses.COLS // 2 - 20,
                        "Unknown distro! Try again...",
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

                    # Display warning about the unknown key and attempt count
                    window.addstr(
                        warning_line,
                        curses.COLS // 2 - 20,
                        "Unknown key! Try again (Attempts left: {})".format(
                            MAX_WRONG_ATTEMPTS - wrong_attempts
                        ),
                    )
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
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        linux_distribution = get_linux_distro(window)
        window.getch()
        hide_output = get_hide_output_choice(window)

        current_row = 0
        print_menu(window, current_row)

        while True:
            key = window.getch()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(packages)

            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % len(packages)

            elif key == 9:  # TAB key
                selected_status[current_row] = not selected_status[current_row]

            elif key == 10:  # Enter key
                window.clear()
                selected_entities = [
                    status
                    for idx, status in enumerate(packages)
                    if selected_status[idx]
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
                if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
                    for idx, entity in enumerate(selected_entities):
                        curses.curs_set(0)  # Hide the cursor
                        window.clear()
                        window.refresh()
                        if "Docker & Docker Desktop" in entity:
                            window.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                "Docker and Docker Desktop installing\n",
                            )
                            get_linux_package_manager(
                                linux_distribution, "docker", hide_output
                            )

                        elif "Podman & Podman Desktop" in entity:
                            window.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                "Podman and Podman Desktop installing",
                            )
                            get_linux_package_manager(
                                linux_distribution, "podman", hide_output
                            )

                        elif "Qemu & Virtual Manager" in entity:
                            window.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                "Qemu & Virtual Manager installing",
                            )
                            get_linux_package_manager(
                                linux_distribution, "qemu", hide_output
                            )

                        elif "Virtual Box" in entity:
                            window.addstr(
                                len(selected_entities) + 4 + idx,
                                3,
                                "Virtual Box installing",
                            )
                            get_linux_package_manager(
                                linux_distribution, "virtualbox", hide_output
                            )
                    window.addstr(len(selected_entities) + 6 + idx, 3, "All Applied!")
                    window.refresh()
                    window.getch()
                    break

            print_menu(window, current_row)
    except KeyboardInterrupt:
        window.clear()
        window.addstr(
            curses.LINES // 2,
            curses.COLS // 2 - 20,
            "Ctrl + C pressed. Exiting...",
        )
        window.addstr(
            curses.LINES // 2 + 2,
            curses.COLS // 2 - 5,
            "Bye 👋",
        )
        window.refresh()
        curses.delay_output(3000)
        exit(1)


curses.wrapper(main)
