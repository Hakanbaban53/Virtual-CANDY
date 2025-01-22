from logging import error
from time import sleep
from requests import get, ConnectionError, Timeout

def check_linux_package_manager_connection(distribution):
    package_manager_urls = {
        "ubuntu": "https://packages.ubuntu.com/",
        "fedora": "https://apps.fedoraproject.org/packages/",
        "debian": "https://packages.debian.org/",
        "arch": "https://archlinux.org/packages/",
    }

    if distribution in package_manager_urls:
        url = package_manager_urls[distribution]
        try:
            response = get(url, timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except Timeout:
            return False
        except ConnectionError:
            return False
    else:
        error(f"Unsupported distribution: {distribution}")
        sleep(5)
        exit(1)
