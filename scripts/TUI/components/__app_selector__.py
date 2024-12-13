import curses

from functions.__get_os_package_manager__ import get_linux_package_manager

from scripts.TUI.components.__print_apps__ import PrintApps

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
            color_pair_default = (
                curses.color_pair(8) if self.use_dark_mode else curses.color_pair(16)
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
                    selection = self.selections.selections(self.use_dark_mode, prompt, x, y, self.height, self.width, OPTIONS_YES_NO)

                    if selection == "Yes":
                        curses.reset_shell_mode()

                        for idx, entity in enumerate(selected_entities):
                            self.stdscr.clear()
                            action_message = f"{entity} {action}ing...\n"
                            self.stdscr.addstr(
                                1,
                                0,
                                action_message,
                                color_pair_default | curses.A_BOLD | curses.A_UNDERLINE,
                            )
                            self.stdscr.refresh()
                            get_linux_package_manager(
                                linux_distribution, entity, output, action
                            )
                            curses.napms(1500)

                        curses.reset_prog_mode()
                        self.stdscr.clear()
                        self.header.display(self.use_dark_mode)
                        self.footer.display(self.use_dark_mode)

                        success_message = "The selected options have been implemented!"
                        reboot_message = "Reboot for the installed apps to appear in the app menu and work properly!"
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
                            color_pair_default | curses.A_BOLD,
                        )
                        self.stdscr.getch()
                        break

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