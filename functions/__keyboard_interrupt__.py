import curses

def main(stdscr):
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

def keyboard_interrupt():
    curses.wrapper(main)