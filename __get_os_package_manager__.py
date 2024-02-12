import distro
import json
from linux_distros.__arch__ import arch_package_installer
from linux_distros.__debian__ import debian_package_installer
from linux_distros.__fedora__ import fedora_package_installer


def get_linux_distribution():
    """Determine the Linux distribution."""
    try:
        return distro.id().lower()
    except FileNotFoundError:
        return None


def get_linux_package_manager():

    linux_distribution = get_linux_distribution()

    print(f"{linux_distribution}")

    with open("packages.json", "r") as json_file:
        instructions_data = json.load(json_file)

    if linux_distribution in instructions_data:
        if linux_distribution == "arch":
            arch_package_installer(instructions_data[linux_distribution])
        elif linux_distribution == "debian":
            debian_package_installer(instructions_data[linux_distribution])
        elif linux_distribution == "fedora":
            fedora_package_installer(instructions_data[linux_distribution])
        else:
            print("ASD")
    else:
        print("No installation instructions found for the detected Linux distribution.")
