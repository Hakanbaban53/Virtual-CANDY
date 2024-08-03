from argparse import ArgumentParser
from functions.__get_os_package_manager__ import identify_distribution

class ArgumentHandler:
    def __init__(self):
        self.args = self.parse_arguments()
        self.adjust_arguments()
        if self.args.distribution and self.args.verbose:
            self.print_info()

    def parse_arguments(self):
        """
        Parse command-line arguments.

        Returns:
            argparse.Namespace: Parsed command-line arguments.
        """
        linux_distro_id = identify_distribution()
        parser = ArgumentParser(description="Linux Package Manager")

        # Add command-line arguments
        parser.add_argument(
            "--distribution", default=linux_distro_id, help="Linux distribution"
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Install or remove all available packages",
        )
        parser.add_argument(
            "-a",
            "--action",
            choices=["install", "remove"],
            default="install",
            help="Install or remove package",
        )
        parser.add_argument(
            "-r",
            "--refresh",
            action="store_true",
            help="Refresh the JSON data regardless of file age",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output for detailed information",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Perform a dry run without making any changes",
        )
        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List available packages for the specified distribution",
        )
        parser.add_argument(
            "packages",
            nargs="*",
            help="List of packages to install or remove.",
        )
        return parser.parse_args()

    def adjust_arguments(self):
        """
        Adjust parsed arguments for consistency.
        """
        # No need for specific adjustments as we are using verbose mode directly

    def print_info(self):
        """Print information about the selected packages and configuration."""

        print("Linux Distribution:", self.args.distribution)
        print("Action: Install" if self.args.action == "install" else "Action: Remove")
        print("Selected Packages:", self.args.packages)
        print("Refresh JSON Data:", self.args.refresh)
        print("Verbose Mode:", self.args.verbose)
        print("Dry Run:", self.args.dry_run)
        print("List Packages:", self.args.list)
        print("All Packages:", self.args.all)
        
    def get_args(self):
        return self.args
