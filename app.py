from __arguments__ import parse_arguments
from __get_os_package_manager__ import get_linux_package_manager


def app():
    args = parse_arguments()

    try:
        if args.distribution and (args.packages or args.install or args.silent):
            #Non-curses logic based on command-line arguments
            print("Linux Distribution:", args.distribution)
            print("Install Packages:", args.install)
            print("Silent Mode:", args.silent)
            print("Selected Packages:", args.packages)

            for package in args.packages:
                print(package)
                get_linux_package_manager(args.distribution, package, args.silent)

        else:
            import __command_GUI__
            

    except KeyboardInterrupt:
        print("Ctrl + C pressed.\nExiting...")


if __name__ == "__main__":
    app()
