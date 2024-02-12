# from __cli_dependencies_install__ import get_dependencies

# if __name__ == "__main__":
#     try:
#         get_dependencies()
#     except KeyboardInterrupt:
#         print("\nCtrl + C pressed\n\nBye 👋.")
#         exit(1)
import platform

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
            return 'Fedora'
        elif 'arch' in linux_distribution.lower():
            return 'Arch'
        elif 'debian' in linux_distribution.lower():
            return 'Debian'
        elif 'ubuntu' in linux_distribution.lower():
            return 'Ubuntu'
        else:
            return 'Unknown Linux distribution'
    else:
        return 'Not running on Linux'

if platform.system() == 'Linux':
    distribution = identify_distribution()
    print(f"Linux distribution: {distribution}")
else:
    print(f"Your system is running {platform.system()}.")
