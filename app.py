import curses
from __get_os_package_manager__ import get_linux_distribution, identify_distribution, get_linux_package_manager

MAX_WRONG_ATTEMPTS = 3

statuses = ["Docker & Docker Desktop", "Podman & Podman Desktop", "Qemu & Virtual Manager", "Virtual Box"]
selected_status = [False] * len(statuses)

def clidependencies(stdscr):
    stdscr.addstr(3, 3, "Detecting CLI dependencies")

def print_menu(stdscr, selected_row):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    for idx, status in enumerate(statuses):
        x = width // 2 - len(status) // 2
        y = height // 2 - len(statuses) // 2 + idx
        if idx == selected_row:
            stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            stdscr.addstr(y, x, status, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x - 3, "(*)" if selected_status[idx] else "( )")
            stdscr.addstr(y, x, status)
    stdscr.refresh()

def get_user_input(stdscr, prompt):
    curses.echo()
    stdscr.addstr(len(statuses) + 5, 0, prompt)
    stdscr.refresh()
    input_str = stdscr.getstr().decode("utf-8")
    return input_str

def get_hide_output_choice(window):
    while True:
        window.addstr(3, 3,"Do you want to hide package manager output? (Enter H/h for hide, N/n for not hide): ")
        window.refresh()
        choice = window.getch()
        if choice in [ord('H'), ord('h')]:
            return True
        elif choice in [ord('N'), ord('n')]:
            return False
        else:
            window.addstr(4, 3,"\nInvalid choice. Please enter H/h or N/n.\n")

def spinning_icon(window, pause_event):
    icons = ['-', '\\', '|', '/']
    i = 0
    while not pause_event.is_set():
        window.addstr(0, 0, f"Installing... {icons[i]}", curses.A_BOLD)
        window.refresh()
        i = (i + 1) % len(icons)
        curses.napms(200)  # Sleep for 200 milliseconds
    window.addstr(0, 0, "Installation paused... ", curses.A_BOLD)
    window.refresh()

def get_linux_distro(stdscr):
    stdscr.clear()
    stdscr.addstr(3, 3, "Getting Linux Distro")
    linux_distribution = get_linux_distribution()
    linux_distro_id = identify_distribution()
    stdscr.addstr(4, 3, "Linux Distro : {}\n   Distro id : {}\n   It's true [Y/n]?".format(linux_distribution, linux_distro_id))

    confirmation_key = stdscr.getch()

    if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
        stdscr.addstr(5, 3, "Now loading the packages...")
        return linux_distro_id
    elif confirmation_key in [78, 110]:  # 'N', 'n'

        wrong_attempts = 0

        while True:
            linux_distribution = get_user_input(stdscr, "Please enter the distro: ")
            linux_distribution_lower = linux_distribution.lower()

            stdscr.addstr(6, 3, "Entered Linux Distro: {}".format(linux_distribution))

            if 'arch' in linux_distribution_lower or 'manjaro' in linux_distribution_lower:
                return 'arch'
            elif 'debian' in linux_distribution_lower:
                return 'debian'
            elif 'fedora' in linux_distribution_lower or 'nobara' in linux_distribution_lower:
                return 'fedora'
            elif 'ubuntu' in linux_distribution_lower or 'linux mint' in linux_distribution_lower:
                return 'ubuntu'
            else:
                stdscr.clear()
                stdscr.addstr(8, 3, "Unknown distro! Try again...")
                wrong_attempts += 1

                if wrong_attempts >= MAX_WRONG_ATTEMPTS:
                    stdscr.clear()
                    stdscr.addstr(9, 3, "Too many wrong attempts. Exiting in 3 seconds...")
                    stdscr.refresh()
                    curses.delay_output(3000)
                    exit(1)

    stdscr.refresh()


def main(stdscr):
    try:
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)


        linux_distribution = get_linux_distro(stdscr)

        hide_output = get_hide_output_choice(stdscr)

        current_row = 0
        print_menu(stdscr, current_row)

        while True:
            key = stdscr.getch()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(statuses)

            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % len(statuses)

            elif key == 9:  # TAB key
                selected_status[current_row] = not selected_status[current_row]

            elif key == 10:  # Enter key
                stdscr.clear()
                selected_entities = [status for idx, status in enumerate(statuses) if selected_status[idx]]
                stdscr.addstr(1, 3, "Selected applications :")
                stdscr.addstr(0, 0, "{}".format(linux_distribution))


                for idx, entity in enumerate(selected_entities):
                    stdscr.addstr(2 + idx, 3, entity)

                stdscr.addstr(len(selected_entities) + 3, 3, "Do you want to continue[Y/n]? \n")
                stdscr.refresh()
                confirmation_key = stdscr.getch()
                if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
                    for idx, entity in enumerate(selected_entities) :
                        curses.curs_set(0)  # Hide the cursor
                        stdscr.clear()
                        stdscr.refresh()
                        if "Docker & Docker Desktop" in entity:
                            stdscr.addstr(len(selected_entities) + 4 + idx, 3, "Docker and Docker Desktop installing\n")
                            get_linux_package_manager(linux_distribution, "docker", hide_output)

                        elif "Podman & Podman Desktop" in entity:
                            stdscr.addstr(len(selected_entities) + 4 + idx, 3, "Podman and Podman Desktop installing")
                            get_linux_package_manager(linux_distribution, "podman", hide_output)

                        elif "Qemu & Virtual Manager" in entity:
                            stdscr.addstr(len(selected_entities) + 4 + idx, 3, "Qemu & Virtual Manager installing")
                            get_linux_package_manager(linux_distribution, "qemu", hide_output)

                        elif "Virtual Box" in entity:
                            stdscr.addstr(len(selected_entities) + 4 + idx, 3, "Virtual Box installing")
                            get_linux_package_manager(linux_distribution, "virtualbox", hide_output)
                    stdscr.addstr(len(selected_entities) + 6 + idx, 3, "All Aplied!")
                    stdscr.refresh()    
                    stdscr.getch()
                    break






            print_menu(stdscr, current_row)
    except KeyboardInterrupt:
        print("\nCtrl + C pressed\n\nBye 👋.")
        exit(1)

curses.wrapper(main)
