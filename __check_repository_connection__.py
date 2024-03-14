from time import sleep
import requests

def check_linux_package_manager_connection(distribution):
    package_manager_urls = {
        "ubuntu": "https://packages.ubuntu.com/",
        "fedora": "https://apps.fedoraproject.org/packages/",
        "debian": "https://packages.debian.org/",
        "arch": "https://archlinux.org/packages/",
    }

    if distribution in package_manager_urls:
        print("Package manager checking internet connection...")
        url = package_manager_urls[distribution]
        try:
            requests.get(url, timeout=5)
            print(f"{distribution.capitalize()} package manager is connected.")
        except requests.ConnectionError:
            print(f"{distribution.capitalize()} package manager is not connected.")
            sleep(5)
            exit(1)
    else:
        print(f"Unsupported distribution: {distribution}")
        sleep(5)
        exit(1)

