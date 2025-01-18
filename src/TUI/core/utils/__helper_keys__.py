from curses import KEY_RESIZE, color_pair

from TUI.core.components.__modal__ import Modal
from TUI.core.static.__data__ import APP_NAME, APP_VERSION, DEVELOPER_NAME, GITHUB_URL, toggle_dark_mode


class HelperKeys:
    def __init__(self, stdscr, resize_handler, header, footer):
        self.stdscr = stdscr
        self.resize_handler = resize_handler
        self.header = header
        self.footer = footer
        self.update_colors()
        self.modal = Modal(self.stdscr)
        self.screen_stack = []  # Stack for navigation

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def keys(self, key, **kwargs):
        if key == 8:  # Ctrl + H for Help    
            self.screen_stack.append("help")
            self.show_help()

        elif key == 1:  # Ctrl + A for About
            self.screen_stack.append("about")
            self.show_about()

        elif key == 4:  # Ctrl + D for Toggle Dark Mode
            toggle_dark_mode()
            if 'update_kwargs' in kwargs and callable(kwargs['update_kwargs']):
                kwargs['update_kwargs']()
            self.update_colors()
            self.header.display()
            self.footer.display()

        elif key == KEY_RESIZE:
            self.resize_handler.resize_handler()

        elif key == 27:  # ESC for Back
            if self.screen_stack:
                self.screen_stack.pop()
                if self.screen_stack:
                    if self.screen_stack[-1] == "help":
                        self.show_help()
                    elif self.screen_stack[-1] == "about":
                        self.show_about()
                else:
                    self.stdscr.clear()
                    self.header.display()
                    self.footer.display()
                    self.stdscr.refresh()

    def show_help(self):
        """Display the Help menu."""
        titlw = "Help Menu"
        content = [
            "Ctrl + H: Toggle Help",
            "Ctrl + D: Toggle Dark Mode",
            "Ctrl + A: About",
        ]
        self.modal.draw_modal(titlw, content)
        

    def show_about(self):
        """Display the About menu."""
        title = "About this App"
        content = [
            f"App Name:{APP_NAME}", 
            f"Version: {APP_VERSION}",
            f"Developed by: {DEVELOPER_NAME}",
            f"Project URL:{GITHUB_URL}",      
                    ]
        self.modal.draw_modal(title, content)
