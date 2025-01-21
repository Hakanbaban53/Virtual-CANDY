from logging import info, debug
from subprocess import PIPE, run
from core.__command_handler__ import run_command
from core.__constants__ import PACKAGE_MANAGER_INSTALL, PACKAGE_MANAGER_REMOVE, PACKAGE_MANAGER_CHECK

def handle_standard_package(distro, package, check_value, action, dry_run, verbose):
    """
    Handles installation or removal of standard packages.

    Args:
        distro (str): Target Linux distribution.
        package (dict): Package metadata.
        check_value (str): Package(s) to check.
        action (str): 'install' or 'remove'.
        dry_run (bool): Simulate actions if True.
        verbose (bool): Verbose output.
    """
    check_cmd = PACKAGE_MANAGER_CHECK[distro]
    check_values = check_value.split()
    installed, not_installed = [], []

    for value in check_values:
        try:
            result = run(f"{check_cmd} {value}", shell=True, stdout=PIPE, stderr=PIPE)
            if value.lower() in result.stdout.decode("utf-8").lower():
                installed.append(value)
            else:
                not_installed.append(value)
        except Exception:
            not_installed.append(value)

    debug(f"Installed: {installed}, Not installed: {not_installed}")

    if action == "install" and not_installed:
        info(f"Installing {package['name']}...")
        if not dry_run:
            command = f"{PACKAGE_MANAGER_INSTALL[distro]} {' '.join(not_installed)}"
            run_command(command, verbose)
    elif action == "remove" and installed:
        info(f"Removing {package['name']}...")
        if not dry_run:
            command = f"{PACKAGE_MANAGER_REMOVE[distro]} {' '.join(installed)}"
            run_command(command, verbose)
