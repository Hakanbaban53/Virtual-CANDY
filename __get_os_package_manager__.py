import json
from linux_distros.__arch__ import arch_package_installer
from linux_distros.__debian__ import debian_package_installer
from linux_distros.__fedora__ import fedora_package_installer
from linux_distros.__ubuntu__ import ubuntu_package_installer

known_distros = {
    "arch": ["arch", "manjaro"],
    "debian": ["debian"],
    "fedora": ["fedora", "nobara"],
    "ubuntu": ["ubuntu", "linux mint"],
}

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
        for distro, keywords in known_distros.items():
            if any(
                keyword in linux_distribution for keyword in keywords
            ):
                return distro
            else:
                return 'Unknown Linux distribution'
    else:
        return 'Not running on Linux'


def get_linux_package_manager(linux_distribution, package_name, hide_output):

    with open("packages.json", "r") as json_file:
        instructions_data = json.load(json_file)

    if linux_distribution in instructions_data:
        if linux_distribution == "arch":
            package_data_ref = instructions_data[linux_distribution]
            for data in package_data_ref:
                name = data.get("name", "")
                if name == package_name:
                    values = data.get("values", [])
                    arch_package_installer(values, hide_output)
        elif linux_distribution == "debian":
            package_data_ref = instructions_data[linux_distribution]
            for data in package_data_ref:
                name = data.get("name", "")
                if name == package_name:
                    values = data.get("values", [])
                    debian_package_installer(values, hide_output)
        elif linux_distribution == "fedora":
            package_data_ref = instructions_data[linux_distribution]
            for data in package_data_ref:
                name = data.get("name", "")
                if name == package_name:
                    values = data.get("values", [])
                    fedora_package_installer(values, hide_output)
        elif linux_distribution == "ubuntu":
            package_data_ref = instructions_data[linux_distribution]
            for data in package_data_ref:
                name = data.get("name", "")
                if name == package_name:
                    values = data.get("values", [])
                    ubuntu_package_installer(values, hide_output)
    else:
        print("No installation instructions found for the detected Linux distribution.")
