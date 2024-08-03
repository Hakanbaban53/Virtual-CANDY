from linux_distros.__arch__ import arch_package_manager
from linux_distros.__debian__ import debian_package_manager
from linux_distros.__fedora__ import fedora_package_manager
from linux_distros.__ubuntu__ import ubuntu_package_manager
from functions.__get_packages_data__ import PackagesJSONHandler



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
        if 'arch' in linux_distribution.lower():
            return 'arch'
        elif 'debian' in linux_distribution.lower():
            return 'debian'
        elif 'fedora' in linux_distribution.lower():
            return 'fedora'
        elif 'ubuntu' in linux_distribution.lower():
            return 'ubuntu'
        else:
            return 'Unknown Linux distribution'
    else:
        return 'Not running on Linux'


def get_linux_package_manager(linux_distribution, package_name, output, action, dry_run=False):
    handler = PackagesJSONHandler()
    packages_data = handler.load_json_data()

    package_manager_func = globals().get(f"{linux_distribution.lower()}_package_manager")
    if package_manager_func:
        package_data_ref = packages_data.get(linux_distribution, [])
        for data in package_data_ref:
            name = data.get("name", "")
            if package_name in name or package_name in name.lower():
                values = data.get("values", [])
                package_manager_func(values, output, action)
                return
    else:
        print(f"No installation instructions found for {linux_distribution}.")
        exit(1)
