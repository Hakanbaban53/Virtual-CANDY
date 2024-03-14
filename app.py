import __cli_dependencies_install__
from __arguments__ import parse_arguments
from __check_repository_connection__ import check_linux_package_manager_connection
from __get_os_package_manager__ import get_linux_package_manager
from __get_os_package_manager__ import identify_distribution


def app():

    """Main application logic."""

    args = parse_arguments()

    try:
        if args.distribution and args.packages:
            print_info(args)

            for package in args.packages:
                get_linux_package_manager(args.distribution, package, args.output, args.action)
        else:
            import __command_GUI__
    except KeyboardInterrupt:
        print("Ctrl + C pressed.\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

def print_info(args):

    """Print information about the selected packages and configuration."""

    print("Linux Distribution:", args.distribution)
    print("Action: Install" if args.action == "install" else "Action: Remove")
    print("Output Mode: Silent" if args.output else "Output Mode: Noisy")
    print("Selected Packages:", args.packages)

if __name__ == "__main__":
    linux_distro_id = identify_distribution()
    check_linux_package_manager_connection(linux_distro_id)
    app()
