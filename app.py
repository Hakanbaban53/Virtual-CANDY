from time import sleep
from __arguments__ import parse_arguments
from __get_os_package_manager__ import get_linux_package_manager


def app():
    args = parse_arguments()
    # print(args.install)
    # print(args.silent or args.noisy)
    # sleep(10)

    try:
        if args.distribution and args.packages and (args.install or args.remove) and (args.silent or args.noisy):
            # Check for mutually exclusive actions
            if args.install and args.remove:
                print("Error: -i (--install) and -r (--remove) are mutually exclusive.")
                exit(1)

            # Check for mutually exclusive output modes
            if args.silent and args.noisy:
                print("Error: -s (--silent) and -n (--noisy) are mutually exclusive.")
                exit(1)

            # Non-curses logic based on command-line arguments
            print("Linux Distribution:", args.distribution)
            print("Action: Install" if args.install else "Action: Remove" if args.remove else "")
            print("Output Mode: Silent" if args.silent else "Output Mode: Noisy" if args.noisy else "")
            print("Selected Packages:", args.packages)

            for package in args.packages:
                get_linux_package_manager(args.distribution, package, args.silent)

        else:
            import __command_GUI__


            

    except KeyboardInterrupt:
        print("Ctrl + C pressed.\nExiting...")


if __name__ == "__main__":
    app()
