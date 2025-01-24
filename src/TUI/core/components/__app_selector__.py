import curses
from json import dumps
from queue import Queue
from textwrap import wrap
from threading import Thread

from core.__pack_type_handler__ import package_manager
from TUI.core.components.__modal_win__ import ModalWindow
from TUI.core.components.__print_apps__ import PrintApps
from TUI.core.static.__data__ import OPTIONS_YES_NO

class AppSelector:
    def __init__(self, stdscr, app_list, cmd, selections, helper_keys, header):
        self.stdscr = stdscr
        self.app_list = app_list
        self.cmd = cmd
        self.selections = selections
        self.helper_keys = helper_keys
        self.header = header
        self.selected_app = None
        self.modalwindow = ModalWindow(self.stdscr)
        self.update_colors()

    def show_package_info(self, package):
        """Show detailed information about the selected package."""
        # Get package details
        package_name = package.get("name", "N/A")
        package_description = package.get("description", "No description available.")
        package_values = package.get("values", [])


        # Prepare the content for the modalwindow
        content = [f"Package Name: {package_name}"]
        long_content = []
        for idx, value in enumerate(package_values):
            formatted_value = dumps(value, indent=2)  # Format JSON with indentation
            long_content.append(f"Value {idx + 1}:")
            long_content.extend(formatted_value.split("\n"))  # Split into lines for curses
        
        # Calculate the maximum width for the description
        max_width = self.stdscr.getmaxyx()[1] // 2 - 4

        # Wrap the package description to the calculated width
        if len(package_description) > max_width:
            # Split the description into lines while preserving word boundaries
            wrapped_description = wrap(package_description, width=max_width)
            
            # Add the label "Description:" at the start
            long_content.insert(0, "Description:")
            long_content[1:1] = wrapped_description  # Insert the wrapped lines
        else:
            # If it fits within max_width, keep it as a single line
            long_content.insert(0, f"Description: {package_description}")

            
        self.modalwindow.draw_modal("Package Information", content, long_content=long_content)

        while True:
            # Refresh pad display inside the modalwindow
            self.modalwindow.modal_pad.refresh(
                self.modalwindow.pad_top,  # Start row in the pad
                self.modalwindow.pad_left,  # Start column in the pad
                self.modalwindow.modal_y + len(content) + 3,  # Top of visible pad area
                self.modalwindow.modal_x + 1,  # Left of visible pad area
                self.modalwindow.modal_y + self.modalwindow.modal_height - 3,  # Bottom of visible pad area
                self.modalwindow.modal_x + self.modalwindow.modal_width - 2,  # Right of visible pad area
            )

            # Handle user input for scrolling or exiting
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.modalwindow.pad_top > 0:
                self.modalwindow.pad_top -= 2
            elif key == curses.KEY_DOWN and self.modalwindow.pad_top < len(long_content) - self.modalwindow.pad_height:
                self.modalwindow.pad_top += 2
            elif key == curses.KEY_LEFT and self.modalwindow.pad_left > 0:
                self.modalwindow.pad_left -= 2
            elif key == curses.KEY_RIGHT:
                # Ensure we don't scroll past the longest line
                max_line_length = max(len(line) for line in long_content)
                if self.modalwindow.pad_left < max_line_length - (self.modalwindow.modal_width - 2):
                    self.modalwindow.pad_left += 2
            elif key == 27:  # ESC key
                self.modalwindow.close()
                break


    def get_relevant_packages(self, package_list):
        relevant_packages = [package.get("name", "") for package in package_list]
        return relevant_packages

    def print_menu(self, selected_row, relevant_packages, selected_status):
        PrintApps(self.stdscr, self.cmd).print_menu(
            selected_row, relevant_packages, selected_status
        )

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_green = curses.color_pair(5 if DARK_MODE else 14)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.color_pair_magenta = curses.color_pair(7 if DARK_MODE else 16)
        self.color_pair_blue = curses.color_pair(8 if DARK_MODE else 17)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def select_app(
        self,
        package_list,
        selected_status_array,
        action,
        linux_distribution,
        log_stream,
        verbose,
        dry_run,
    ):
        self.cmd.clear_middle_section()
        relevant_packages = self.get_relevant_packages(package_list)
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
                    if idx < curses.LINES - 10:
                        self.stdscr.addstr(
                            4 + idx,
                            curses.COLS // 2 - len(entity) // 2,
                            entity,
                            curses.color_pair(7) | curses.A_BOLD,
                        )
                    else:
                        prompt = "Other selected applications..."
                        self.stdscr.addstr(
                            curses.LINES - 6,
                            curses.COLS // 2 - (len(prompt)) // 2,
                            prompt,
                            curses.color_pair(3) | curses.A_BOLD,
                        )
                        break

                prompt = "Do you want to continue?"
                x = curses.COLS // 2 - len(prompt) // 2
                y = (
                    4 + len(selected_entities)
                    if len(selected_entities) < curses.LINES - 10
                    else curses.LINES - 5
                )
                selection = self.selections.selections(
                    x=x, y=y, question=prompt, options=OPTIONS_YES_NO
                )

                if selection == "Yes":
                    curses.reset_shell_mode()  # Reset terminal mode
                    pad_height = (
                        len(selected_entities) * 500
                    )  # Dynamic height based on the number of selected entities
                    pad_width = (
                        curses.COLS * 2
                    )  # Can be much larger than the terminal size
                    output_pad = curses.newpad(pad_height, pad_width)
                    output_pad.bkgd(self.color_pair_normal | curses.A_REVERSE)
                    output_lines = []  # Store all output lines
                    scroll_offset_vertical = 0  # Current vertical scroll position
                    scroll_offset_horizontal = 0  # Current horizontal scroll position
                    max_lines = (
                        curses.LINES - 6
                    )  # Number of visible lines in the window

                    def render_output():
                        output_pad.refresh(
                            scroll_offset_vertical,
                            scroll_offset_horizontal,
                            2,
                            2,
                            curses.LINES - 3,
                            curses.COLS - 3,
                        )

                    # Use a separate thread to process packages one by one
                    def process_packages():
                        for entity in selected_entities:
                            action_message = f"{entity} {action}ing...\n"
                            log_queue.put(("action", action_message))

                            # Call the installation function
                            package = next(
                                item for item in package_list if item["name"] == entity
                            )
                            package_manager(
                                linux_distribution,
                                package.get("values", []),
                                action,
                                verbose,
                                dry_run,
                            )

                            log_stream.seek(0)
                            for line in log_stream.readlines():
                                log_queue.put(("log", line.strip()))
                            log_queue.put(
                                ("finished", f"{entity} {action}ed successfully.\n")
                            )
                            log_stream.truncate(0)
                            log_stream.seek(0)

                    log_queue = Queue()

                    # Start the processing in a thread
                    processing_thread = Thread(target=process_packages)
                    processing_thread.start()

                    # Main loop to dynamically render log output
                    while processing_thread.is_alive() or not log_queue.empty():
                        if len(output_lines) >= curses.LINES - 6:
                            scroll_offset_vertical += 1
                        msg_type, line = log_queue.get()
                        output_lines.append(line)
                        if msg_type == "action":
                            output_pad.addstr(
                                len(output_lines) - 1,
                                0,
                                line,
                                self.color_pair_blue | curses.A_BOLD | curses.A_REVERSE,
                            )
                        elif msg_type == "finished":
                            output_pad.addstr(
                                len(output_lines) - 1,
                                0,
                                line,
                                self.color_pair_green
                                | curses.A_BOLD
                                | curses.A_REVERSE,
                            )
                        else:
                            output_pad.addstr(
                                len(output_lines) - 1, 0, line, self.color_pair_normal
                            )
                        render_output()

                    # Wait for the processing thread to finish
                    processing_thread.join()

                    # Notify the user that processing is complete
                    finished_message = "Processing completed. Press 'Enter' to exit."
                    output_lines.append(finished_message)
                    output_pad.addstr(
                        len(output_lines),
                        (curses.COLS // 2) - (len(finished_message) // 2),
                        finished_message,
                        self.color_pair_magenta | curses.A_BOLD | curses.A_REVERSE,
                    )
                    curses.reset_prog_mode()  # Reset terminal mode

                    # Wait for user input to exit
                    while True:
                        render_output()
                        key = self.stdscr.getch()
                        if (
                            key == curses.KEY_DOWN
                            and scroll_offset_vertical + max_lines < len(output_lines)
                        ):
                            scroll_offset_vertical += 2
                        elif key == curses.KEY_UP and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= 2
                        elif (
                            key == curses.KEY_NPAGE
                            and scroll_offset_vertical + max_lines < len(output_lines)
                        ):
                            scroll_offset_vertical += max_lines
                        elif key == curses.KEY_PPAGE and scroll_offset_vertical > 0:
                            scroll_offset_vertical -= max_lines
                        elif key == curses.KEY_LEFT and scroll_offset_horizontal > 0:
                            scroll_offset_horizontal -= 2
                        elif (
                            key == curses.KEY_RIGHT
                            and scroll_offset_horizontal < pad_width - curses.COLS
                        ):
                            scroll_offset_horizontal += 2
                        elif key in [10, curses.KEY_ENTER]:  # Optionally handle 'Enter'
                            break
                        else:
                            self.helper_keys.keys(key, update_colors=self.update_colors)

                    self.cmd.clear_middle_section()
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
                    self.stdscr.getch()
                    break
            elif key == ord("i"):  # 'i' key for package info
                selected_package = package_list[current_row]
                self.show_package_info(selected_package)

            else:
                self.helper_keys.keys(key, update_colors=self.update_colors)

            self.print_menu(current_row, relevant_packages, selected_status_array)
