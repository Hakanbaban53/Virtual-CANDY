import argparse
from __get_os_package_manager__ import (
    identify_distribution,
)

def parse_arguments():
    linux_distro_id = identify_distribution()
    parser = argparse.ArgumentParser(description="Linux Package Manager")

    # Add command-line arguments with default values
    parser.add_argument(
        "--distribution", default=linux_distro_id, help="Linux distribution"
    )
    parser.add_argument(
        "-i", "--install", action="store_true", default=False, help="Install packages"
    )
    parser.add_argument(
        "-s", "--silent", action="store_true", default=False, help="Silent mode"
    )
    parser.add_argument(
        "packages",
        nargs="*",
        help="List of packages to install.",
    )

    return parser.parse_args()