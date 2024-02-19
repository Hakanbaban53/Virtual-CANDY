# from __cli_dependencies_install__ import get_dependencies

# if __name__ == "__main__":
#     try:
#         get_dependencies()
        
#     except KeyboardInterrupt:
#         print("\nCtrl + C pressed\n\nBye 👋.")
#         exit(1)

import subprocess
import curses
import threading
import time

def install_package(package_name, window):
    try:
        window.addstr(f"Installing {package_name}... ")
        window.refresh()

        # Your installation command here, for example:
        with open('/dev/null', 'w') as devnull:
            # Your installation command here, for example:
            subprocess.run(['sudo', 'dnf', 'remove', '-y', package_name], check=True, stdout=devnull, stderr=devnull)

        window.addstr("Done!\n")
    except subprocess.CalledProcessError as e:
        window.addstr(f"Error: {e}\n")
    finally:
        window.refresh()

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

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    pause_event = threading.Event()

    # Start the spinning icon in a separate thread
    icon_thread = threading.Thread(target=spinning_icon, args=(stdscr, pause_event))
    icon_thread.daemon = True
    icon_thread.start()

    # Simulate installing packages
    packages_to_install = ['gnome-software']

    for package_name in packages_to_install:
        install_package(package_name, stdscr)

        # Pause the spinning icon thread when sudo password is needed
        pause_event.set()
        stdscr.addstr(0, 0, "Enter sudo password: ", curses.A_BOLD)
        stdscr.refresh()

        # Your code to get sudo password here, for example:
        sudo_password = input()

        # Resume the spinning icon thread after getting the password
        pause_event.clear()

    # Wait for the icon thread to finish
    icon_thread.join()

    stdscr.getch()  # Wait for a key press

if __name__ == "__main__":
    curses.wrapper(main)
