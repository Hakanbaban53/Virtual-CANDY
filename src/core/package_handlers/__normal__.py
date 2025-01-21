from logging import info, debug
from subprocess import PIPE, run
from core.__command_handler__ import run_command
from core.__constants__ import PACKAGE_MANAGER_INSTALL, PACKAGE_MANAGER_REMOVE, PACKAGE_MANAGER_CHECK
from core.package_handlers.__aur__ import handle_aur_package
from core.package_handlers.__local__ import handle_local_package

def handle_standard_package(distro, package, package_type, check_value, action, dry_run, verbose):
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
        info(f"Installing {' '.join(not_installed)}...")
        if not dry_run:
            if package_type in ["package", "url-package"]:
                command = PACKAGE_MANAGER_INSTALL[distro].format(package.get("install_value", ""))
                run_command(command, verbose)
            elif package_type == "local-package":
                handle_local_package(distro, {package.get("install_value", "")}, verbose)
            elif package_type == "AUR-package":
                handle_aur_package(not_installed, verbose)
    elif action == "remove" and installed:
        info(f"Removing {' '.join(installed)}...")
        if not dry_run:
            command = PACKAGE_MANAGER_REMOVE[distro].format({' '.join(installed)})
            run_command(command, verbose)

