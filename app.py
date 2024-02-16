import curses

statuses = ["Docker & Docker Desktop", "Podman & Podman Desktop", "Qemu & Virtual Manager", "Virtual Box"]
selected_status = [False] * len(statuses)

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

def main(stdscr):
    try:
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

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

                for idx, entity in enumerate(selected_entities):
                    stdscr.addstr(2 + idx, 3, entity)

                stdscr.addstr(len(selected_entities) + 3, 3, "Do you want to continue[Y/n]? ")
                stdscr.refresh()
                confirmation_key = stdscr.getch()
                if confirmation_key in [89, 121, 10]:  # 'Y', 'y', Enter
                    stdscr.addstr(len(selected_entities) + 4, 3, "All Aplied! ")
                    stdscr.refresh()
                    stdscr.getch()
                    break

                # for idx, entity in enumerate(selected_entities) :
                #     if "Docker & Docker Desktop" in entity:
                #         result = "Docker and Docker Desktop installing"
                #         stdscr.addstr(len(statuses) + 4 + idx, 0, "Result of multiplication: {}".format(result))

                #     elif "Podman & Podman Desktop" in entity:
                #         stdscr.addstr(len(statuses) + 4 + idx, 0, "Podman and Podman Desktop installing")
                #         stdscr.addstr(len(statuses) + 5 + idx, 0, "Result of multiplication: {}".format(result))

                    # elif "Qemu & Virtual Manager" in entity:
                    #     stdscr.addstr(len(statuses) + 6 + idx, 0, "Qemu & Virtual Manager installing")
                    #     stdscr.addstr(len(statuses) + 7 + idx, 0, "Result of multiplication: {}".format(result))

                    # elif "Virtual Box" in entity:
                    #     stdscr.addstr(len(statuses) + 8 + idx, 0, "Virtual Box installing")
                    #     stdscr.addstr(len(statuses) + 9 + idx, 0, "Result of multiplication: {}".format(result))


            print_menu(stdscr, current_row)
    except KeyboardInterrupt:
        print("\nCtrl + C pressed\n\nBye 👋.")
        exit(1)

curses.wrapper(main)
