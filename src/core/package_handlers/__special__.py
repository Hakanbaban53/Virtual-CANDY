from genericpath import exists
from logging import debug, error, info
from posixpath import dirname

from core.__command_handler__ import run_command
from core.__constants__ import CACHE_PATH


def special_package_installer(package, check_script, action, dry_run, verbose):
    """
    Handles special-package installation logic.

    Args:
        distro (str): The target distribution.
        package (dict): Package metadata.
        check_script (list): Commands or paths to check the state.
        action (str): Action to perform ('install' or 'remove').
        dry_run (bool): If True, only simulate actions.
        verbose (file-like): If True, suppress verbose.
    """
    special_values = package.get("special_values", [])
    install_script = package.get("install_script", [])
    remove_script = package.get("remove_script", [])
    app_name = package.get("name", "unknown")
    script_executed = False
    for script in check_script:
        if (exists(script) or dirname(script)) and script != "":
            script_executed = True
            break

    try:
        if action == "install":
            info(f"Installing {app_name}...")

            if script_executed:
                info("App already installed. Skipping...")
                return

            # Replace placeholders with values dynamically
            for special_value in special_values:
                for key, value in special_value.items():
                    install_script = [
                        cmd.replace(f"${key}", value) for cmd in install_script
                    ]

            # Replace $CACHE_PATH explicitly
            install_script = [
                cmd.replace("$CACHE_PATH", str(CACHE_PATH)) for cmd in install_script
            ]

            # Execute install scripts
            for command in install_script:
                if dry_run:
                    debug(f"Would execute: {command}")
                else:
                    run_command(command, verbose)

            info(f"{app_name} installation completed.")

        elif action == "remove":
            info(f"Removing {app_name}...")

            if not script_executed:
                info("App not installed. Skipping...")
                return

            for special_value in special_values:
                for key, value in special_value.items():
                    remove_script = [
                        cmd.replace(f"${key}", value) for cmd in remove_script
                    ]

            # Replace $CACHE_PATH in remove scripts
            remove_script = [
                cmd.replace("$CACHE_PATH", str(CACHE_PATH)) for cmd in remove_script
            ]

            # Execute remove scripts
            for command in remove_script:
                if dry_run:
                    debug(f"Would execute: {command}")
                else:
                    run_command(command, verbose)

            info(f"{app_name} removal completed.")
    except Exception as e:
        error(f"An error occurred while handling {app_name}: {e}")