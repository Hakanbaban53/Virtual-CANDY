import curses


class ColorManager:
    def __init__(self):
        self.color_mapping = {
            "dark_mode": {
                "default": 2,  # White on black
                "error": 3,    # Red on black
                "highlight": 4,  # Cyan on black
                "success": 5,  # Green on black
                "warning": 6,  # Yellow on black
                "info": 7,     # Magenta on black
                "special": 8,  # Blue on white
                "inverse": 9,  # White on blue
            },
            "light_mode": {
                "default": 11,  # Black on white
                "error": 12,    # Red on white
                "highlight": 13,  # Cyan on white
                "success": 14,  # Green on white
                "warning": 15,  # Yellow on white
                "info": 16,     # Magenta on white
                "special": 17,  # Blue on black
                "inverse": 18,  # Black on blue
            },
        }

    def initialize_colors(self):
        """
        Initialize all colors in curses.
        """
        for color in self.dark_mode_colors + self.light_mode_colors:
            curses.init_pair(*color)

    def get_color(self, name, dark_mode):
        """
        Get the color pair based on the name and mode.
        :param name: Logical name of the color (e.g., 'default', 'error').
        :param dark_mode: Boolean indicating if dark mode is active.
        :return: The curses color pair ID.
        """
        mode = "dark_mode" if dark_mode else "light_mode"
        color_id = self.color_mapping[mode].get(name, self.color_mapping[mode]["default"])
        return curses.color_pair(color_id)
