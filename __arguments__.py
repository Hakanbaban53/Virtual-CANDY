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

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "-i", "--install", action="store_true", default=None, help="Install packages"
    )
    action_group.add_argument(
        "-r", "--remove", action="store_true", default=None, help="Remove packages"
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-s", "--silent", action="store_true", default=None, help="Silent mode"
    )
    output_group.add_argument(
        "-n", "--noisy", action="store_true", default=None, help="Noisy mode"
    )

    parser.add_argument(
        "packages",
        nargs="*",
        help="List of packages to install.",
    )

    args = parser.parse_args()

    if (
        args.install is None
        and args.remove is None
        and args.silent is None
        and args.noisy is None
    ):
        args.install, args.silent = True, True

    elif args.install and args.noisy:
        args.install, args.noisy = True, True
    elif args.remove and args.noisy:
        args.noisy, args.remove = True, True

    elif args.remove or args.install:
        args.silent = True
    elif args.silent or args.noisy:
        args.install = True

    return args
