from time import sleep

from core.__command_handler__ import run_command
from core.__constants__ import CACHE_PATH


def handle_aur_package(packages, verbose):
    for install_value in packages:
        repository_directory = f"{CACHE_PATH}/{install_value}"
        run_command(
            command=f"git clone https://aur.archlinux.org/{install_value}.git",
            verbose=verbose,
            cwd=CACHE_PATH,
        )
        sleep(1)
        run_command(
            command=f"makepkg -si --noconfirm",
            verbose=verbose,
            cwd=repository_directory,
        )
        sleep(1)
        run_command(
            command=f"rm -rf {repository_directory}",
            verbose=verbose,
        )