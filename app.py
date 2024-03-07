from time import sleep
from __arguments__ import parse_arguments
from __check_repository_connection__ import check_connection
from __get_os_package_manager__ import get_linux_package_manager


def app():
    args = parse_arguments()

    try:
        if args.distribution and args.packages:

            # Non-curses logic based on command-line arguments
            print("Linux Distribution:", args.distribution)
            print("Action: Install" if args.action == "install" else "Action: Remove")
            print("Output Mode: Silent" if args.output else "Output Mode: Noisy")
            print("Selected Packages:", args.packages)

            for package in args.packages:
                get_linux_package_manager(args.distribution, package, args.output, args.action)

        else:
            import __command_GUI__

    except KeyboardInterrupt:
        print("Ctrl + C pressed.\nExiting...")


if __name__ == "__main__":

    # check_connection()

    app()
