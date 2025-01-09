import curses

class PrintApps:
    def __init__(self, stdscr, use_dark_mode, width, height, cmd):
        self.stdscr = stdscr
        self.use_dark_mode = use_dark_mode
        self.width = width
        self.height = height
        self.cmd = cmd
    
    def print_menu(self, selected_row, relevant_packages, selected_status, MAX_DISPLAYED_PACKAGES):
        self.cmd.clear_middle_section()
        
        header_color = curses.color_pair(6 if self.use_dark_mode else 15)
        row_color = curses.color_pair(2 if self.use_dark_mode else 11)
        selected_row_color = (
            curses.color_pair(5 if self.use_dark_mode else 14) | curses.A_REVERSE
        )

        # Draw headers
        table_width = min(self.width - 4, 80)
        table_start_y = 2
        table_start_x = self.width // 2 - table_width // 2

        headers = ["Status", "Package Name"]
        col_width = (table_width - 4) // len(headers)
        for i, header in enumerate(headers):
            x = table_start_x + 7 + i * (col_width - 1)
            self.stdscr.addstr(table_start_y, x, header, header_color)

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

            color = selected_row_color if idx == selected_row else row_color
            self.stdscr.addstr(y, table_start_x + 2, status.ljust(19), color)
            self.stdscr.addstr(y, table_start_x + 25, package_name.ljust(49), color)

        # Draw arrows
        if start_idx > 0:
            self.stdscr.addstr(
                table_start_y + 2,
                table_start_x + 22,
                "/\\",
                curses.A_BOLD | header_color,
            )
        if end_idx < len(relevant_packages):
            self.stdscr.addstr(
                table_start_y + len(relevant_packages) - 2,
                table_start_x + 22,
                "\\/",
                curses.A_BOLD | header_color,
            )

        self.stdscr.refresh()