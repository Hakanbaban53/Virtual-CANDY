import curses

from TUI.core.static.__data__ import MAX_DISPLAYED_PACKAGES

class PrintApps:
    def __init__(self, stdscr, cmd):
        self.stdscr = stdscr
        self.cmd = cmd
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = curses.color_pair(2 if DARK_MODE else 11)
        self.color_pair_red = curses.color_pair(3 if DARK_MODE else 12)
        self.color_pair_yellow = curses.color_pair(6 if DARK_MODE else 15)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()
    
    def print_menu(self, selected_row, relevant_packages, selected_status):
        self.cmd.clear_middle_section()
        height, width = self.stdscr.getmaxyx()
        
        # Draw headers
        table_width = min(width - 4, 80)
        table_start_y = 2
        table_start_x = width // 2 - table_width // 2

        headers = ["Status", "Package Name"]
        col_width = (table_width - 4) // len(headers)
        for i, header in enumerate(headers):
            x = table_start_x + 7 + i * (col_width - 1)
            self.stdscr.addstr(table_start_y, x, header, self.color_pair_yellow)

        # Draw horizontal line under headers
        self.stdscr.hline(
            table_start_y + 1, table_start_x + 1, curses.ACS_HLINE, table_width - 2
        )

        start_idx = max(0, selected_row - MAX_DISPLAYED_PACKAGES // 2)
        end_idx = min(len(relevant_packages), start_idx + MAX_DISPLAYED_PACKAGES)

        for idx in range(start_idx, end_idx):
            y = table_start_y + idx - start_idx + 2
            status = "[X] Selected" if selected_status[idx] else "[ ] Unselected"
            package_name = relevant_packages[idx].replace("_", " ")

            color = (self.color_pair_normal | curses.A_REVERSE) if idx == selected_row else self.color_pair_normal
            self.stdscr.addstr(y, table_start_x + 2, status.ljust(19), color)
            self.stdscr.addstr(y, table_start_x + 25, package_name.ljust(49), color)

        # Draw arrows
        if start_idx > 0:
            self.stdscr.addstr(
                table_start_y + 2,
                table_start_x + 22,
                "/\\",
                self.color_pair_yellow | curses.A_BOLD,
            )
        if end_idx < len(relevant_packages):
            self.stdscr.addstr(
                table_start_y + len(relevant_packages) - 2,
                table_start_x + 22,
                "\\/",
                self.color_pair_yellow | curses.A_BOLD,
            )

        self.stdscr.refresh()