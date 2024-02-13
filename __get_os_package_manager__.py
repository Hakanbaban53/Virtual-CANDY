import json
from linux_distros.__arch__ import arch_package_installer
from linux_distros.__debian__ import debian_package_installer
from linux_distros.__fedora__ import fedora_package_installer



def get_linux_distribution():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('PRETTY_NAME'):
                    _, distro_info = line.split('=')
                    return distro_info.strip().strip('"')
    except FileNotFoundError:
        return None

def identify_distribution():
    linux_distribution = get_linux_distribution()

    if linux_distribution:
        if 'fedora' in linux_distribution.lower():
            return 'fedora'
        elif 'arch' in linux_distribution.lower():
            return 'arch'
        elif 'debian' in linux_distribution.lower():
            return 'debian'
        elif 'ubuntu' in linux_distribution.lower():
            return 'ubuntu'
        else:
            return 'Unknown Linux distribution'
    else:
        return 'Not running on Linux'


def get_linux_package_manager():

    linux_distribution = identify_distribution()

    print(f"{linux_distribution}")

    with open("packages.json", "r") as json_file:
        instructions_data = json.load(json_file)

    if linux_distribution in instructions_data:
        if linux_distribution == "arch":
            arch_package_installer(instructions_data[linux_distribution])
        elif linux_distribution == "ubuntu":
            debian_package_installer(instructions_data[linux_distribution])
        elif linux_distribution == "fedora":
            fedora_package_installer(instructions_data[linux_distribution])
        else:
            print("ASD")
    else:
        print("No installation instructions found for the detected Linux distribution.")
