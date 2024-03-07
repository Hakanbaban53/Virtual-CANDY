import argparse
from __get_os_package_manager__ import identify_distribution

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    linux_distro_id = identify_distribution()
    parser = argparse.ArgumentParser(description="Linux Package Manager")

    # Add command-line arguments with default values
    parser.add_argument(
        "--distribution", default=linux_distro_id, help="Linux distribution"
    )
    parser.add_argument(
        "-a", "--action", choices=["install", "remove"], default="install", help="Install or remove package"
    )
    parser.add_argument(
        "-o", "--output", choices=["silent", "noisy"], default="silent", help="Silent or noisy mode"
    )
    parser.add_argument(
        "packages",
        nargs="*",
        help="List of packages to install.",
    )

    args = parser.parse_args()

    adjust_arguments(args)

    return args

def adjust_arguments(args):
    """
    Adjust parsed arguments for consistency.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    if args.action == "install" and args.output == "silent":
        args.action, args.output = "install", True
    elif args.action == "install" and args.output == "noisy":
        args.output = False  # Reset noisy since it's not applicable in silent mode
    elif args.action == "remove" and args.output == "noisy":
        args.output = False  # Reset noisy since it's not applicable in silent mode
    elif args.action == "remove" or args.action == "install":
        args.output = True
    elif args.output == "noisy" or args.output == "silent":
        args.action = "install"