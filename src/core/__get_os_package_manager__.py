def get_linux_pretty_name():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('PRETTY_NAME'):
                    _, distro_info = line.split('=')
                    return distro_info.strip().strip('"')
    except FileNotFoundError:
        return None

def identify_distribution():
    linux_distribution = get_linux_pretty_name()

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

