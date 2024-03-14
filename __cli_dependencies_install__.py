import subprocess
from time import sleep

dependencies = ['requests']


def check_dependencies(dependencies):
    """Check if required Python packages are installed."""
    missing_packages = []

    for package in dependencies:
        try:
            result = subprocess.run(
                ["pip", "show", package], stdout=subprocess.PIPE, check=True, text=True
            )
            if "Version" not in result.stdout:
                missing_packages.append(package)
            else:
                print(package, "is installed.")
        except subprocess.CalledProcessError:
            missing_packages.append(package)

    return missing_packages


def install_dependencies(dependencies):
    """Install missing Python packages using pip."""
    if dependencies:
        print("Installing missing dependencies...")
        subprocess.run(["pip", "install"] + dependencies, check=True)
        print("Dependencies installed successfully.")
    else:
        print("No missing dependencies.")


def handle_dependencies():
    missing_packages = check_dependencies(dependencies)

    if missing_packages:
        confirmation_key = input("Do you want to install them? (Y/n): ")
        if confirmation_key.lower() in ['y', 'yes', '']:
            install_dependencies(missing_packages)
            print("All dependencies installed!")
            sleep(2)
        else:
            print("Operation aborted. Exiting...")
            sleep(3)
            exit(1)
    else:
        print("All dependencies are already installed.")
        sleep(2)


handle_dependencies()