from logging import info, error
import os
from subprocess import CalledProcessError
from core.__constants__ import CACHE_PATH, PACKAGE_MANAGER_INSTALL_LOCAL, PACKAGE_TYPES
from core.__command_handler__ import run_command


def handle_local_package(distro, install_value, verbose):
    """
    Handles downloading and installing local packages.

    Args:
        distro (str): Target Linux distribution.
        install_value (str): URL or file path for the package.
        verbose (file-like): Verbose output.
    """
    if distro not in PACKAGE_MANAGER_INSTALL_LOCAL:
        raise ValueError(f"Unsupported distribution: {distro}")

    CACHE_PATH.mkdir(parents=True, exist_ok=True)  # Ensure the cache directory exists
    package_ext = PACKAGE_TYPES[distro]
    local_path = CACHE_PATH / f"local.package.{package_ext}"

    try:
        # Download the package
        run_command(
            f"wget --progress=bar:force -O {local_path} {install_value}",
            cwd=str(CACHE_PATH),
            verbose=verbose,
        )

        # Install the package
        run_command(
            f"{PACKAGE_MANAGER_INSTALL_LOCAL[distro]} {local_path}",
            verbose=verbose,
        )

        # Handle additional steps for certain distros
        if os.path.exists("/etc/debian_version"):
            run_command("sudo apt-get install -f -y", verbose=verbose)

        info(f"Successfully installed local package from {install_value}.")

    except CalledProcessError as err:
        error(f"An error occurred: {err}")

    finally:
        # Cleanup the downloaded package
        if local_path.exists():
            local_path.unlink()
            info(f"Cleaned up temporary package file: {local_path}")
