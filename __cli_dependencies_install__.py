import subprocess
from __pip_install__ import pip_package_installer
from __get_os_package_manager__ import get_linux_package_manager

dependencies = ["pip"]


def check_dependencies():
    """Install required dependencies for the CLI app if not already installed."""

    for package in dependencies:
        try:
            # Check if the package is installedY
            return subprocess.check_call(
                ["pip", "show", package], stdout=subprocess.PIPE
            )
        except subprocess.CalledProcessError:
            # If an error occurs, the package is not installed, so install it
            return False


def get_dependencies():
    dependencies_installed = check_dependencies()

    if dependencies_installed:
        print("All dependencies installed!")
        get_linux_package_manager()
    else:
        selection = (
            input(
                "Dependencies were not satisfied. Would you like to download? (Y/n): "
            )
            .strip()
            .lower()
        )
        if selection.lower() == "y" or not selection:
            pip_package_installer(dependencies)
            get_linux_package_manager()
        elif selection.lower() == "n":
            print("Can you want to continue installing[y/N] ?")
        else:
            print("Operation aborted.")
