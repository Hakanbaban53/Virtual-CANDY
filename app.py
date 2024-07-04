from functions.__cli_dependencies_install__ import DependencyManager
from scripts.__arguments__ import parse_arguments
from functions.__check_repository_connection__ import check_linux_package_manager_connection
from functions.__get_os_package_manager__ import get_linux_package_manager
from functions.__get_os_package_manager__ import identify_distribution
from scripts.__terminal_UI__ import start_terminal_ui


def app():

    """Main application logic."""

    args = parse_arguments()

    try:
        
        if args.distribution and args.packages:
            if args.action == 'install':
                linux_distro_id = identify_distribution()
                check_linux_package_manager_connection(linux_distro_id)

            for package in args.packages:
                get_linux_package_manager(args.distribution, package, args.output, args.action)

        else:
            start_terminal_ui()
            
    except KeyboardInterrupt:
        print("Ctrl + C pressed.\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    DependencyManager().handle_dependencies()
    app()

