from curses import (
    color_pair,
    A_BOLD,
    A_UNDERLINE,
    A_REVERSE,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_ENTER,
    KEY_RESIZE,
)

from TUI.core.static.__data__ import toggle_dark_mode


class Selections:
    def __init__(self, stdscr, resize_handler, clean_line, footer, header):
        self.stdscr = stdscr
        self.resize_handler = resize_handler
        self.clean_line = clean_line
        self.footer = footer
        self.header = header
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.stdscr.bkgd(self.color_pair_normal)

        self.stdscr.refresh()

    def selections(self, prompt, x, y, options):
        # Handle user selections
        selected_option = 0
        height, width = self.stdscr.getmaxyx()

        while True:
            # Clear previous prompt
            self.clean_line.clean_line(x, y)

            # Display prompt centered horizontally
            prompt_x = width // 2 - len(prompt) // 2
            self.stdscr.addstr(
                y,
                prompt_x,
                prompt,
                self.color_pair_normal | A_BOLD | A_UNDERLINE,
            )

            # Calculate the starting x position to center the options
            total_options_width = (
                sum(len(option) + 4 for option in options) + (len(options) - 1) * 2
            )
            options_x = width // 2 - total_options_width // 2

            for i, option in enumerate(options):
                option_x = options_x + (len(option) + 6) * i
                option_y = y + 2
                if i == selected_option:
                    self.stdscr.addstr(
                        option_y, option_x, "[" + option + "]", A_REVERSE
                    )
                else:
                    self.stdscr.addstr(option_y, option_x, "[" + option + "]")

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == KEY_LEFT:
                selected_option = (selected_option - 1) % len(options)
            elif key == KEY_RIGHT:
                selected_option = (selected_option + 1) % len(options)
            elif key in [KEY_ENTER, 10, 13]:
                return options[selected_option]
            elif key == 4:  # Ctrl + D for toggle dark/light mode
                toggle_dark_mode()
                self.update_colors()
                self.stdscr.refresh()
                self.header.display()
                self.footer.display()
            elif key == KEY_RESIZE:
                self.resize_handler.resize_handler()
