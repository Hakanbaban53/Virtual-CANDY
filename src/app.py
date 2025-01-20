import io
import logging
from core.__logging_manager__ import LoggingManager
from core.__check_repository_connection__ import check_linux_package_manager_connection
from core.__get_os_package_manager__ import (
    get_linux_package_manager,
    identify_distribution,
    get_linux_pretty_name,
)
from core.__get_packages_data__ import PackagesJSONHandler
from TUI.__terminal_UI__ import start_terminal_ui
from utils.cli.__arguments__ import ArgumentHandler


class PackageManagerApp:
    def __init__(self):
        # Initialize argument handler and load JSON data
        self.linux_distro_id = identify_distribution()
        self.linux_pretty_name = get_linux_pretty_name()

        self.args = ArgumentHandler(self.linux_distro_id)
        self.get_args = self.args.get_args()
        self.log_stream = io.StringIO()
        LoggingManager(self.get_args.verbose, self.get_args.dry_run, self.log_stream)

        self.json_handler = PackagesJSONHandler(
            json_file_path=self.get_args.json, json_file_url=self.get_args.url
        )
        self.packages_data = self.json_handler.load_json_data(
            refresh=self.get_args.refresh
        )

    def packages(self, linux_distro):
        """Get relevant packages for the given Linux distribution."""
        if linux_distro in self.packages_data:
            return [
                package.get("name", "") for package in self.packages_data[linux_distro]
            ]
        return []

    def run(self):
        """Run the main application logic."""
        try:
            # Handle package actions (install/remove)
            if self.get_args.packages or self.get_args.list or self.get_args.all:
                relevant_packages = self.packages(self.get_args.distribution)
                if self.get_args.distribution and self.get_args.verbose:
                    self.args.print_info()

                if self.get_args.list:
                    self.args.print_relevant_packages(relevant_packages)
                    return

                user_packages = set(self.get_args.packages)
                valid_packages = [
                    pkg for pkg in user_packages if pkg in relevant_packages
                ]
                valid_packages = (
                    relevant_packages if self.get_args.all else valid_packages
                )

                self.args.print_verbose_package_info(relevant_packages, valid_packages)

                if self.get_args.action == "install" and not self.get_args.dry_run:
                    logging.info("Checking package manager connection...")
                    status = check_linux_package_manager_connection(
                        self.get_args.distribution
                    )
                    if not status:
                        logging.error(
                            "Failed to connect to package manager repository. Exiting..."
                        )
                        return

                if valid_packages:
                    for package in valid_packages:
                        print("\n========================================")
                        print(f"Processing package: {package}")
                        print("========================================\n")

                        get_linux_package_manager(
                            linux_distribution=self.get_args.distribution,
                            package_name=package,
                            output=self.get_args.verbose,
                            action=self.get_args.action,
                            dry_run=self.get_args.dry_run,
                        )
                else:
                    logging.warning(
                        "No valid packages found for the specified distribution."
                    )
            else:
                start_terminal_ui(
                    self.get_args.distribution,
                    self.linux_pretty_name,
                    self.packages_data,
                    self.log_stream,
                    self.get_args.verbose,
                    self.get_args.dry_run,
                )

        except KeyboardInterrupt:
            print("\nCtrl + C pressed. Exiting...")
            print("Goodbye 👋")
        except RuntimeError as re:
            logging.error(f"Runtime error: {re}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = PackageManagerApp()
    app.run()
