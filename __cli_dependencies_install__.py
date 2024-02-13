import subprocess
from __pip_install__ import pip_package_installer
from __get_os_package_manager__ import get_linux_package_manager

dependencies = ["click"]


def check_dependencies():
    """Install required dependencies for the CLI app if not already installed."""

    dependencies = ["pip"]

    for package in dependencies:
        try:
            subprocess.check_call(["pip", "show", package], stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            # If an error occurs
            if "externally-managed-environment" in str(e):
                print("Error: externally-managed-environment detected. Removing the file and retrying.")
                subprocess.run(['sudo', 'rm', '/usr/lib/python3.11/EXTERNALLY-MANAGED'])
                check_dependencies()
            else:
                return False
    return True 


def get_dependencies():
    dependencies_installed = check_dependencies()
    print(dependencies_installed)

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
