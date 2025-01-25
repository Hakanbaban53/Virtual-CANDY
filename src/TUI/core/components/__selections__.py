from curses import (
    color_pair,
    A_BOLD,
    A_UNDERLINE,
    A_REVERSE,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_ENTER,
)

class Selections:
    def __init__(self, stdscr, clean_line, helper_keys):
        self.stdscr = stdscr
        self.clean_line = clean_line
        self.helper_keys = helper_keys
        self.update_colors()

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.color_pair_yellow = color_pair(6 if DARK_MODE else 15)

        self.stdscr.bkgd(self.color_pair_normal)

        self.stdscr.refresh()

    def selections(self, x, y, question, options, **kwargs):
        # Handle user selections
        selected_option = 0
        height, width = self.stdscr.getmaxyx()

        while True:

            # Handle multiple prompts if provided
            if 'prompts' in kwargs:
                prompts = kwargs['prompts']
                for i, prompt in enumerate(prompts):
                    prompt_x = width // 2 - len(prompt) // 2
                    self.stdscr.addstr(
                        y - len(prompts) + i,
                        prompt_x,
                        prompt,
                        self.color_pair_normal,
                    )
            # Clear previous prompt
            self.clean_line.clean_line(x, y + 1)

            # Display prompt centered horizontally
            prompt_x = width // 2 - len(question) // 2
            self.stdscr.addstr(
                y + 1,
                prompt_x,
                question,
                self.color_pair_yellow | A_BOLD | A_UNDERLINE,
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
            else:
                self.helper_keys.keys(key, update_colors=self.update_colors)
