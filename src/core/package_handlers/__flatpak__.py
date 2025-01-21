from logging import debug, error, info
from subprocess import PIPE, run

from core.__command_handler__ import run_command

def handle_flatpak_repo(package, dry_run, verbose):
    install_value = package.get("install_value", "")
    try:
        info(f"Adding Flatpak repository: {install_value}")
        if not dry_run:
            run_command(command=f"flatpak remote-add --if-not-exists {install_value}", verbose=verbose)
    except Exception as e:
        error(f"An error occurred: {e}")

def handle_flatpak_package(package, check_value, action, dry_run, verbose):
    package_name = package.get("name", "")
    check_values = check_value.split()
    installed, not_installed = [], []

    for value in check_values:
        try:
            result = run(f"flatpak list --app --columns=name --columns=ref | grep {value}", shell=True, stdout=PIPE, stderr=PIPE)
            if value in result.stdout.decode("utf-8"):
                installed.append(value)
            else:
                not_installed.append(value)
        except Exception:
            not_installed.append(value)

            debug(f"Installed: {installed}, Not installed: {not_installed}")

            if action == "install" and not_installed:
                info(f"Installing {package_name}...")
                if not dry_run:
                    command = f"flatpak install -y {package_name}"
                    run_command(command, verbose)
            elif action == "remove" and installed:
                info(f"Removing {package_name}...")
                if not dry_run:
                    command = f"flatpak uninstall -y {package_name}"
                    run_command(command, verbose)