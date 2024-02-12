from __cli_dependencies_install__ import get_dependencies

if __name__ == "__main__":
    try:
        get_dependencies()
    except KeyboardInterrupt:
        print("\nCtrl + C pressed\n\nBye 👋.")
        exit(1)
