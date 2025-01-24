from colorama import Fore, Style
from argparse import ArgumentParser, RawTextHelpFormatter

class ArgumentHandler:
    def __init__(self, linux_distro_id):
        # Parse arguments and adjust them
        self.linux_distro_id = linux_distro_id
        self.args = self.parse_arguments()
        self.adjust_arguments()

    def parse_arguments(self):
        """Parse command-line arguments."""
        parser = ArgumentParser(description="Virtual Candy (VCANDY)", formatter_class=RawTextHelpFormatter)

        # Add command-line arguments
        parser.add_argument(
            "--distribution", default=self.linux_distro_id, help="Linux distribution"
        )
        parser.add_argument(
            "-a",
            "--action",
            choices=["install", "remove"],
            default="install",
            help="Install or remove package",
        )
        parser.add_argument(
            "-j", "--json", help="URL or path to JSON file containing package data"
        )
        parser.add_argument(
            "-u",
            "--url",
            help="URL to JSON file containing package data. Its need to be used with -r",
        )
        parser.add_argument(
            "-r",
            "--refresh",
            action="store_true",
            help="Refresh the JSON data regardless of file age",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose output"
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
            "--all",
            action="store_true",
            help="Install or remove all available packages",
        )
        parser.add_argument(
            "packages", nargs="*", help="List of packages to install or remove."
        )
        parser.add_argument(
            "--version",
            action="version",
            version=(
                "Virtual Candy (VCANDY) Version 2.2.8\n"
                "License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.\n"
                "This is free software: you are free to change and redistribute it.\n"
                "There is NO WARRANTY, to the extent permitted by law.\n"
                "\nWritten by Hakan İSMAİL."
            ),
        )

        return parser.parse_args()

    def adjust_arguments(self):
        """Adjust parsed arguments for consistency."""
        # No adjustments are needed at the moment as we use arguments directly

    def format_bool(self, value):
        """Format boolean values as Yes/No."""
        return "Yes" if value else "No"

    def print_info(self):
        """Print general information about the arguments."""
        print(40 * f"={Fore.BLUE}")
        print(
            f"{Fore.CYAN}Linux Distribution ID:{Style.RESET_ALL} {self.args.distribution}"
        )
        print(
            f"{Fore.GREEN}Action:{Style.RESET_ALL} {'Install' if self.args.action == 'install' else 'Remove'}"
        )
        print(
            f"{Fore.LIGHTRED_EX}JSON File:{Style.RESET_ALL} {'Default' if not self.args.json else self.args.json}"
        )
        print(
            f"{Fore.LIGHTMAGENTA_EX}Custom URL:{Style.RESET_ALL} {'None' if not self.args.url else self.args.url}"
        )
        print(
            f"{Fore.YELLOW}Selected Packages:{Style.RESET_ALL} {', '.join(self.args.packages)}"
        )
        print(
            f"{Fore.MAGENTA}Refresh JSON Data:{Style.RESET_ALL} {self.format_bool(self.args.refresh)}"
        )
        print(
            f"{Fore.BLUE}Verbose Mode:{Style.RESET_ALL} {self.format_bool(self.args.verbose)}"
        )
        print(
            f"{Fore.RED}Dry Run:{Style.RESET_ALL} {self.format_bool(self.args.dry_run)}"
        )
        print(
            f"{Fore.WHITE}List Packages:{Style.RESET_ALL} {self.format_bool(self.args.list)}"
        )
        print(
            f"{Fore.LIGHTYELLOW_EX}All Packages:{Style.RESET_ALL} {self.format_bool(self.args.all)}"
        )
        print(40 * f"={Fore.BLUE}")

    def print_relevant_packages(self, relevant_packages):
        """Print the relevant packages for the distribution."""
        print(f"{Fore.CYAN}Relevant Packages for Distribution:{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}{', '.join(f'[{package}]' for package in relevant_packages)}{Style.RESET_ALL}"
        )

    def print_verbose_package_info(self, relevant_packages, valid_packages):
        """Print verbose information about relevant and filtered packages."""
        if self.args.verbose:
            print(f"{Fore.CYAN}Relevant Packages for Distribution:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{', '.join(relevant_packages)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Filtered Packages to be Processed:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{', '.join(valid_packages)}{Style.RESET_ALL}")

    def get_args(self):
        """Return the parsed arguments."""
        return self.args
