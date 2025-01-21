from logging import error
from os import path
from posixpath import join
from subprocess import CalledProcessError
from core.__constants__ import PACKAGE_TYPES
from core.__command_handler__ import run_command


def handle_local_package(install_value, distro, CACHE_PATH, verbose):

    if distro not in PACKAGE_TYPES:
        raise ValueError(f"Unsupported distribution: {distro}")

    package_type = PACKAGE_TYPES[distro]
    local_path = join(CACHE_PATH, f"local.package.{package_type}")

    try:
        run_command(
            f"wget --progress=bar:force -O {local_path} {install_value}",
            cwd=CACHE_PATH,
            verbose=verbose,
        )

        if distro == "arch":
            run_command(
                f"sudo pacman -U {local_path} --noconfirm",
                verbose=verbose,
                cwd=local_path,
            )
        elif distro in {"debian", "ubuntu"}:
            run_command(
                f"sudo dpkg -i {local_path}",
                verbose=verbose,
                cwd=local_path,
            )
            run_command(
                f"sudo apt-get install -f -y",
                verbose=verbose,
                cwd=local_path,
            )
        elif distro == "fedora":
            run_command(
                f"sudo dnf install {local_path} -y",
                verbose=verbose,
                cwd=local_path,
            )
    except CalledProcessError as err:
        error(f"An error occurred: {err}")
    finally:
        if path.exists(local_path):
            run_command(f"rm -rf {local_path}", verbose=verbose)