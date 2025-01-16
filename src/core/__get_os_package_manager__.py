from utils.installer.__combined__ import package_manager
from core.__get_packages_data__ import PackagesJSONHandler

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
        distro_lower = linux_distribution.lower()
        if 'arch' in distro_lower:
            return 'arch'
        elif 'debian' in distro_lower:
            return 'debian'
        elif 'fedora' in distro_lower:
            return 'fedora'
        elif 'ubuntu' in distro_lower:
            return 'ubuntu'
        else:
            return 'Unknown Linux distribution'
    else:
        return 'Not running on Linux'

def get_linux_package_manager(linux_distribution, package_name, output, action, dry_run=False):
    handler = PackagesJSONHandler()
    packages_data = handler.load_json_data()

    if not packages_data:
        print("Failed to load packages data.")
        return

    package_manager_func = package_manager
    if not package_manager_func:
        print(f"No installation instructions found for {linux_distribution}.")
        return

    package_data_ref = packages_data.get(linux_distribution, [])
    for data in package_data_ref:
        name = data.get("name", "").lower()
        if package_name.lower() in name:
            values = data.get("values", [])
            package_manager_func(linux_distribution, values, output, action, dry_run)
            return

    print(f"No matching package found for {package_name} in {linux_distribution}.")
