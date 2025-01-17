import curses
import io
from queue import Queue
import threading

from TUI.core.components.__print_apps__ import PrintApps
from core.__get_os_package_manager__ import get_linux_package_manager
from core.__logging_manager__ import LoggingManager


class AppSelector:
    def __init__(self, stdscr, app_list, width, height, use_dark_mode, cmd, selections, header, footer, resize_handler):
        self.stdscr = stdscr
        self.width = width
        self.height = height
        self.app_list = app_list
        self.use_dark_mode = use_dark_mode
        self.cmd = cmd
        self.selections = selections
        self.header = header
        self.footer = footer
        self.resize_handler = resize_handler
        self.selected_app = None

    def print_menu(self, selected_row, relevant_packages, selected_status, MAX_DISPLAYED_PACKAGES):
        PrintApps(self.stdscr, self.use_dark_mode, self.width, self.height, self.cmd).print_menu(
            selected_row, relevant_packages, selected_status, MAX_DISPLAYED_PACKAGES
        )
    
    def select_app(self, relevant_packages, selected_status_array, action, linux_distribution, output, OPTIONS_YES_NO, MIN_COLS, MIN_LINES, MAX_DISPLAYED_PACKAGES):
            package_name = (
                curses.color_pair(9) if self.use_dark_mode else curses.color_pair(18)
            )
            outputs_color = (
                 curses.color_pair(2) if self.use_dark_mode else curses.color_pair(11)
            )
            finished_color = (
                 curses.color_pair(7) if self.use_dark_mode else curses.color_pair(16)
            )
            self.cmd.clear_middle_section()
            self.print_menu(0, relevant_packages, selected_status_array, MAX_DISPLAYED_PACKAGES)
            current_row = 0

            while True:
                key = self.stdscr.getch()

                if key == curses.KEY_DOWN:
                    current_row = (current_row + 1) % len(relevant_packages)

                elif key == curses.KEY_UP:
                    current_row = (current_row - 1) % len(relevant_packages)

                elif key == 9:  # TAB key
                    selected_status_array[current_row] = (
                        not selected_status_array[current_row]
                    )

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
                    selection = self.selections.selections(self.use_dark_mode, prompt, x, y, self.height, self.width, OPTIONS_YES_NO, MIN_COLS, MIN_LINES)

                    if selection == "Yes":
                        pad_height = 100  # Can be much larger than the terminal size
                        pad_width = curses.COLS - 4
                        output_pad = curses.newpad(pad_height, pad_width)
                        output_pad.bkgd(' ', curses.A_REVERSE)
                        output_lines = []  # Store all output lines
                        scroll_offset = 0  # Current scroll position
                        max_lines = curses.LINES - 6  # Number of visible lines in the window
                        self.stdscr.nodelay(True)

                        def render_output():
                            output_pad.refresh(scroll_offset, 0, 2, 2, curses.LINES - 3, curses.COLS - 3)

                        # Use a separate thread to process packages one by one
                        def process_packages():
                            for entity in selected_entities:
                                action_message = f"{entity} {action}ing...\n"
                                log_queue.put(("action", action_message))
                                log_stream = io.StringIO()
                                LoggingManager(verbose=True, dry_run=False, log_stream=log_stream)

                                # Call the installation function
                                get_linux_package_manager(linux_distribution, entity, output, action)

                                log_stream.seek(0)
                                for line in log_stream.readlines():
                                    log_queue.put(("log", line.strip() + "\n"))
                                log_queue.put(("action", f"{entity} {action}ed successfully.\n"))
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
                                    output_pad.addstr(len(output_lines), 0, line, package_name)
                                else:
                                    output_pad.addstr(len(output_lines), 0, line, outputs_color)
                                render_output()

                            # Handle user input for scrolling
                            key = self.stdscr.getch()
                            if key == curses.KEY_DOWN and scroll_offset + max_lines < len(output_lines):
                                scroll_offset += 1
                                render_output()
                            elif key == curses.KEY_UP and scroll_offset > 0:
                                scroll_offset -= 1
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
                        output_lines.append("Processing completed. Use arrow keys to scroll. Press 'q' to exit.")
                        output_pad.addstr(len(output_lines), 0, "Processing completed. Use arrow keys to scroll. Press 'q' to exit.", finished_color)
                        render_output()

                        self.stdscr.nodelay(False)
                        # Wait for user input to exit
                        while True:
                            key = self.stdscr.getch()
                            if key == curses.KEY_DOWN and scroll_offset + max_lines < len(output_lines):
                                scroll_offset += 1
                                render_output()
                            elif key == curses.KEY_UP and scroll_offset > 0:
                                scroll_offset -= 1
                                render_output()
                            elif key == ord("q"):  # Exit on 'q'
                                break
                            elif key in [10, curses.KEY_ENTER]:  # Optionally handle 'Enter'
                                break
                            else:
                                # Ignore other keys
                                continue

                        render_output()

                        curses.reset_prog_mode()
                        self.stdscr.clear()
                        self.header.display(self.use_dark_mode)
                        self.footer.display(self.use_dark_mode)

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
                            package_name | curses.A_BOLD,
                        )


                elif key == 4:  # Ctrl + D for toggle dark/light mode
                    self.use_dark_mode = not self.use_dark_mode
                    self.stdscr.bkgd(
                        curses.color_pair(2)
                        if self.use_dark_mode
                        else curses.color_pair(11)
                    )
                    self.stdscr.refresh()
                    self.header.display(self.use_dark_mode)
                    self.footer.display(self.use_dark_mode)
                    self.print_menu(
                        current_row, relevant_packages, selected_status_array, MAX_DISPLAYED_PACKAGES
                    )
                elif key == curses.KEY_RESIZE:
                    self.resize_handler.resize_handler(
                        self.use_dark_mode, self.width, self.height, MIN_COLS, MIN_LINES
                    )

                self.print_menu(
                    current_row, relevant_packages, selected_status_array, MAX_DISPLAYED_PACKAGES
                )