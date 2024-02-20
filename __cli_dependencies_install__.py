import subprocess
from __pip_install__ import pip_package_installer
from __get_os_package_manager__ import get_linux_package_manager

dependencies = ["halo"]


def check_dependencies():
    """Install required dependencies for the CLI app if not already installed."""

    for package in dependencies:
        try:
            subprocess.check_call(["pip", "show", package], stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return False
    return True


def get_dependencies():
    dependencies_installed = check_dependencies()
    print(dependencies_installed)

    if dependencies_installed:
        print("All dependencies installed!")
        get_linux_package_manager()
    else:
        selection = input(
            "Dependencies were not satisfied. Would you like to download? (Y/n): "
        )
        if selection in [89, 121, 10]:  # 'Y', 'y', Enter
            pip_package_installer(dependencies)
        elif selection.lower() == "n":
            print("Can you want to continue installing[y/N] ?")
        else:
            print("Operation aborted.")
