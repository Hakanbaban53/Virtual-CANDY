OPTIONS_YES_NO = ["Yes", "No"]
OPTIONS_INSTALL_REMOVE = ["install", "remove"]

MIN_LINES = 20
MIN_COLS = 80
MAX_DISPLAYED_PACKAGES = 15

APP_NAME = "VCANDY"
APP_VERSION = "V3.0"
DEVELOPER_NAME = "Hakan İSMAİL"
GITHUB_URL = "https://github.com/Hakanbaban53/Virtual-CANDY"


def is_system_dark_mode():
    try:
        from subprocess import run

        # Check GNOME
        cmd_gnome = "gsettings get org.gnome.desktop.interface color-scheme"
        result_gnome = run(cmd_gnome, shell=True, capture_output=True, text=True)
        if "dark" in result_gnome.stdout:
            return True

        # Check KDE
        cmd_kde = "lookandfeeltool --list"
        result_kde = run(cmd_kde, shell=True, capture_output=True, text=True)
        if "dark" in result_kde.stdout:
            return True

        # Check XFCE
        cmd_xfce = "xfconf-query -c xsettings -p /Net/ThemeName"
        result_xfce = run(cmd_xfce, shell=True, capture_output=True, text=True)
        if "dark" in result_xfce.stdout.lower():
            return True

        return False
    except Exception:
        return False


DARK_MODE = is_system_dark_mode()


def toggle_dark_mode():
    global DARK_MODE
    DARK_MODE = not DARK_MODE


FOOTER_TEXT = [
    "[^C Exit]",
    "[^H Help]",
]

KNOWN_DISTROS = {
    "arch": ["arch"],
    "debian": ["debian"],
    "fedora": ["fedora"],
    "ubuntu": ["ubuntu"],
}
