from scripts.__arguments__ import ArgumentHandler
from functions.__check_repository_connection__ import (
    check_linux_package_manager_connection,
)
from functions.__get_os_package_manager__ import (
    get_linux_package_manager,
)
from scripts.__terminal_UI__ import start_terminal_ui
from functions.__get_packages_data__ import PackagesJSONHandler


class PackageManagerApp:
    def __init__(self):
        self.args = ArgumentHandler().get_args()
        self.json_handler = PackagesJSONHandler()
        self.packages_data = self.json_handler.load_json_data(refresh=self.args.refresh)

    def packages(self, linux_distro):
        if linux_distro in self.packages_data:
            package_list = self.packages_data[linux_distro]
            relevant_packages = [package.get("name", "") for package in package_list]
            return relevant_packages
        else:
            return []

    def run(self):
        """Run the main application logic."""
        try:

            if self.args.packages or self.args.list or self.args.all:
                relevant_packages = self.packages(self.args.distribution)

                if self.args.list:
                    print("Relevant packages for distribution:", relevant_packages)
                    return

                user_packages = set(self.args.packages)
                valid_packages = [
                    pkg for pkg in user_packages if pkg in relevant_packages
                ]

                valid_packages = relevant_packages if self.args.all else valid_packages

                if self.args.verbose:
                    print("Relevant packages for distribution:", relevant_packages)
                    print("Filtered packages to be processed:", valid_packages)

                if self.args.action == "install":
                    print("Checking package manager connection...")
                    stasus = check_linux_package_manager_connection(
                        self.args.distribution
                    )
                    if not stasus:
                        print(
                            "Failed to connect to package manager repository. Exiting..."
                        )
                        return

                if valid_packages:
                    for package in valid_packages:
                        print("\n========================================")
                        print(f"Processing package: {package}")
                        print("========================================\n")

                        get_linux_package_manager(
                            linux_distribution=self.args.distribution,
                            package_name=package,
                            output=self.args.verbose,
                            action=self.args.action,
                            dry_run=self.args.dry_run,
                        )
                else:
                    print("No valid packages found for the specified distribution.")

            else:
                start_terminal_ui()

        except KeyboardInterrupt:
            print("\nCtrl + C pressed. Exiting...")
            print("Goodbye 👋")
        except RuntimeError as re:
            print(f"Runtime error: {re}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = PackageManagerApp()
    app.run()
