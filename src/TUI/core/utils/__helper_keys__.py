from curses import KEY_RESIZE, color_pair

from TUI.core.components.__modal_win__ import ModalWindow
from TUI.core.static.__data__ import APP_NAME, APP_VERSION, DEVELOPER_NAME, GITHUB_URL, toggle_dark_mode

class HelperKeys:
    def __init__(self, stdscr, resize_handler, header, footer):
        self.stdscr = stdscr
        self.resize_handler = resize_handler
        self.header = header
        self.footer = footer
        self.modalwindow = ModalWindow(self.stdscr)
        self.update_colors()
        self.modal_showing = False

    def update_colors(self):
        from TUI.core.static.__data__ import DARK_MODE

        self.color_pair_normal = color_pair(2 if DARK_MODE else 11)
        self.modalwindow.update_colors()
        self.stdscr.bkgd(self.color_pair_normal)
        self.stdscr.refresh()

    def keys(self, key, **kwargs):
        """Handle key inputs."""
        if key == 8:  # Ctrl + H for Help
            if not self.modal_showing:
                self.show_help()
        elif key == 1:  # Ctrl + A for About
            if not self.modal_showing:
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

    def show_help(self):
        """Display the Help modal."""
        content = [
            "Ctrl + H: Help",
            "Ctrl + D: Toggle Dark Mode",
            "Ctrl + A: About",
            "Arrow keys: Navigate",
            "TAB: Select/Unselect Package",
            "i: Package Info",
            "Enter: Install/Remove Selected Packages",
            "Ctrl + C: Exit",
        ]
        self.modalwindow.draw_modal("Help Menu", content)
        
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC for Back
                self.modalwindow.close()
                self.modal_showing = False
                break
            else:
                pass

    def show_about(self):
        """Display the About modal."""
        content = [
            f"App Name: {APP_NAME}",
            f"Version: {APP_VERSION}",
            f"Developer: {DEVELOPER_NAME}",
            f"Project URL: {GITHUB_URL}",
        ]
        self.modalwindow.draw_modal("About This App", content)

        while True:        
            key = self.stdscr.getch()
            if key == 27:  # ESC for Back
                self.modalwindow.close()
                self.modal_showing = False
                break
            else:
                pass


