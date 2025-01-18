import curses
import io
from queue import Queue
import threading

from TUI.core.components.__print_apps__ import PrintApps
from TUI.core.static.__data__ import OPTIONS_YES_NO, toggle_dark_mode
from core.__get_os_package_manager__ import get_linux_package_manager
from core.__logging_manager__ import LoggingManager


class AppSelector:
    def __init__(
        self, stdscr, app_list, cmd, selections, helper_keys
    ):
        self.stdscr = stdscr
        self.app_list = app_list
        self.cmd = cmd
        self.selections = selections
        self.helper_keys = helper_keys
        self.selected_app = None
        self.update_colors()

    def print_menu(self, selected_row, relevant_packages, selected_status):
        PrintApps(self.stdscr, self.cmd).print_menu(
            selected_row, relevant_packages, selected_status
        )

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_magenta = curses.color_pair(7 if DARK_MODE else 16)
        self.color_pair_blue = curses.color_pair(8 if DARK_MODE else 17)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def select_app(
        self,
        relevant_packages,
        selected_status_array,
        action,
        linux_distribution,
        output,
    ):
        self.cmd.clear_middle_section()
        self.print_menu(0, relevant_packages, selected_status_array)
        current_row = 0

        while True:
            key = self.stdscr.getch()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(relevant_packages)

            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % len(relevant_packages)

            elif key == 9:  # TAB key
                selected_status_array[current_row] = not selected_status_array[
                    current_row
                ]

            elif key == 10:  # Enter key
                self.cmd.clear_middle_section()
                selected_entities = [
                    status
                    for idx, status in enumerate(relevant_packages)
                    if selected_status_array[idx]
                ]

                if not selected_entities:
                    self.stdscr.addstr(
                        curses.LINES // 2,
                        curses.COLS // 2 - 12,
                        "Please select packages!",
                        curses.color_pair(3) | curses.A_BOLD,
                    )
                    self.stdscr.addstr(
                        curses.LINES // 2 + 2,
                        curses.COLS // 2 - 17,
                        "[Press any arrow key to continue]",
                    )
                    continue

                prompt_selected = "Selected applications:"
                self.stdscr.addstr(
                    2,
                    curses.COLS // 2 - len(prompt_selected) // 2,
                    prompt_selected,
                    curses.color_pair(6) | curses.A_BOLD,
                )

                for idx, entity in enumerate(selected_entities):
                    self.stdscr.addstr(
                        3 + idx,
                        curses.COLS // 2 - len(entity) // 2,
                        entity,
                    )

                prompt = "Do you want to continue?"
                x = curses.COLS // 2 - len(prompt) // 2
                y = 4 + len(selected_entities)
                selection = self.selections.selections(prompt, x, y, OPTIONS_YES_NO)

                if selection == "Yes":
                    pad_height = 100  # Can be much larger than the terminal size
                    pad_width = curses.COLS * 2  # Can be much larger than the terminal size
                    output_pad = curses.newpad(pad_height, pad_width)
                    output_pad.bkgd(self.color_pair_normal | curses.A_REVERSE)
                    output_lines = []  # Store all output lines
                    scroll_offset_vertical = 0  # Current vertical scroll position
                    scroll_offset_horizontal = 0  # Current horizontal scroll position
                    max_lines = (
                        curses.LINES - 6
                    )  # Number of visible lines in the window
                    self.stdscr.nodelay(True)

                    def render_output():
                        output_pad.refresh(
                            scroll_offset_vertical, scroll_offset_horizontal, 2, 2, curses.LINES - 3, curses.COLS - 3
                        )

                    # Use a separate thread to process packages one by one
                    def process_packages():
                        for entity in selected_entities:
                            action_message = f"{entity} {action}ing...\n"
                            log_queue.put(("action", action_message))
                            log_stream = io.StringIO()
                            LoggingManager(
                                verbose=True, dry_run=False, log_stream=log_stream
                            )

                            # Call the installation function
                            get_linux_package_manager(
                                linux_distribution, entity, output, action
                            )

                            log_stream.seek(0)
                            for line in log_stream.readlines():
                                log_queue.put(("log", line.strip() + "\n"))
                            log_queue.put(
                                ("action", f"{entity} {action}ed successfully.\n")
                            )
                            log_stream.truncate(0)
                            log_stream.seek(0)

                    log_queue = Queue()

                    # Start the processing in a thread
                    processing_thread = threading.Thread(target=process_packages)
                    processing_thread.start()

                    # Main loop to dynamically render log output
                    while processing_thread.is_alive() or not log_queue.empty():
                        while not log_queue.empty():
                            msg_type, line = log_queue.get()
                            output_lines.append(line)
                            if msg_type == "action":
                                output_pad.addstr(
                                    len(output_lines), 0, line, self.color_pair_blue | curses.A_BOLD | curses.A_REVERSE
                                )
                            else:
                                output_pad.addstr(
                                    len(output_lines), 0, line, self.color_pair_normal
                                )
                            render_output()

                        # Handle user input for scrolling
                        key = self.stdscr.getch()
                        if key == curses.KEY_DOWN and scroll_offset_vertical + max_lines < len(
                            output_lines
                        ):
                            scroll_offset_vertical += 1
                            render_output()
                        elif key == curses.KEY_UP and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= 1
                            render_output()
                        elif key == curses.KEY_NPAGE and scroll_offset_vertical + max_lines < len(
                            output_lines
                        ):
                            scroll_offset_vertical += max_lines
                            render_output()
                        elif key == curses.KEY_PPAGE and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= max_lines
                            render_output()
                        elif key == curses.KEY_LEFT and scroll_offset_horizontal > 0:
                            scroll_offset_horizontal -= 1
                            render_output()
                        elif key == curses.KEY_RIGHT and scroll_offset_horizontal < pad_width - curses.COLS:
                            scroll_offset_horizontal += 1
                            render_output()
                        elif key == ord("q"):  # Exit on 'q'
                            break
                        elif key in [10, curses.KEY_ENTER]:  # Optionally handle 'Enter'
                            continue
                        else:
                            # Ignore other keys
                            continue

                    # Wait for the processing thread to finish
                    processing_thread.join()

                    # Notify the user that processing is complete
                    output_lines.append(
                        "Processing completed. Use arrow keys to scroll. Press 'q' to exit."
                    )
                    output_pad.addstr(
                        len(output_lines),
                        0,
                        "Processing completed. Use arrow keys to scroll. Press 'q' to exit.",
                        self.color_pair_magenta | curses.A_BOLD | curses.A_REVERSE,
                    )
                    render_output()

                    self.stdscr.nodelay(False)
                    # Wait for user input to exit
                    while True:
                        key = self.stdscr.getch()
                        if key == curses.KEY_DOWN and scroll_offset_vertical + max_lines < len(
                            output_lines
                        ):
                            scroll_offset_vertical += 1
                            render_output()
                        elif key == curses.KEY_UP and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= 1
                            render_output()
                        elif key == curses.KEY_NPAGE and scroll_offset_vertical + max_lines < len(
                            output_lines
                        ):
                            scroll_offset_vertical += max_lines
                            render_output()
                        elif key == curses.KEY_PPAGE and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= max_lines
                            render_output()
                        elif key == curses.KEY_LEFT and scroll_offset_horizontal > 0:
                            scroll_offset_horizontal -= 1
                            render_output()
                        elif key == curses.KEY_RIGHT and scroll_offset_horizontal < pad_width - curses.COLS:
                            scroll_offset_horizontal += 1
                            render_output()
                        elif key == ord("q"):  # Exit on 'q'
                            break
                        elif key in [10, curses.KEY_ENTER]:  # Optionally handle 'Enter'
                            break
                        else:
                            # Ignore other keys
                            continue

                    render_output()

                    success_message = "The selected options have been implemented!"
                    reboot_message = "Some Applications may require a reboot to take effect. (Kernel modules, etc.)"
                    press_any_key = "[Press any key to exit]"
                    self.stdscr.addstr(
                        curses.LINES // 2 - 4,
                        curses.COLS // 2 - len(success_message) // 2,
                        success_message,
                    )
                    self.stdscr.addstr(
                        curses.LINES // 2 - 2,
                        curses.COLS // 2 - len(reboot_message) // 2,
                        reboot_message,
                    )
                    self.stdscr.addstr(
                        curses.LINES // 2,
                        curses.COLS // 2 - len(press_any_key) // 2,
                        press_any_key,
                        self.color_pair_blue | curses.A_BOLD | curses.A_REVERSE,
                    )

            else:
                self.helper_keys.keys(key, update_colors=self.update_colors)


            self.print_menu(current_row, relevant_packages, selected_status_array)
