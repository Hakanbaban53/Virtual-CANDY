from logging import error
from time import sleep
from requests import get, ConnectionError, Timeout

from core.__constants__ import REPOSITORY_URLS

def check_linux_package_manager_connection(distribution):

    if distribution in REPOSITORY_URLS:
        url = REPOSITORY_URLS[distribution]
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
