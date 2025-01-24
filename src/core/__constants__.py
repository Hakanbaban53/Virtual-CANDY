from os import getenv, path
from pathlib import Path

CACHE_PATH = Path(path.expanduser("~")) / ".cache" / "vcandy"
CURRENT_USER = getenv("USER")

REPOSITORY_URLS = {
    "arch": "https://archlinux.org/packages/",
    "debian": "https://packages.debian.org/",
    "fedora": "https://apps.fedoraproject.org/packages/",
    "ubuntu": "https://packages.ubuntu.com/",
}


PACKAGE_TYPES = {
    "arch": "tar.gz",
    "debian": "deb",
    "ubuntu": "deb",
    "fedora": "rpm",
}

PACKAGE_MANAGER_INSTALL = {
    "arch": "sudo pacman -S --noconfirm",
    "debian": "sudo apt-get install -y",
    "ubuntu": "sudo apt-get install -y",
    "fedora": "sudo dnf install -y",
}

PACKAGE_MANAGER_INSTALL_LOCAL = {
    "arch": "sudo pacman -U --noconfirm",
    "debian": "sudo dpkg -i",
    "ubuntu": "sudo dpkg -i",
    "fedora": "sudo dnf install -y",
}

PACKAGE_MANAGER_REMOVE = {
    "arch": "sudo pacman -Rsc --noconfirm",
    "debian": "sudo apt-get remove -y",
    "ubuntu": "sudo apt-get remove -y",
    "fedora": "sudo dnf remove -y",
}

PACKAGE_MANAGER_CHECK = {
    "arch": "pacman -Q",
    "debian": "apt list --installed",
    "ubuntu": "apt list --installed",
    "fedora": "dnf list --installed",
}


PACKAGES_JSON_URL = "https://raw.githubusercontent.com/Hakanbaban53/Virtual-CANDY/refs/heads/main/packages/packages.json"
