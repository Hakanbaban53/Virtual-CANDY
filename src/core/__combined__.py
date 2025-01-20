import logging
import os
from subprocess import run, PIPE, CalledProcessError, check_output
from os import path, getenv, chdir, getcwd
from time import sleep

CACHE_PATH = path.join(path.expanduser("~"), ".cache", "vcandy")

def run_command(command, verbose):
    try:
        completed_process = run([command], capture_output=True, shell=True)
        if completed_process.stderr and verbose:
            logging.error(f"An error occurred: {completed_process.stderr.decode()}")
        elif completed_process.stdout and verbose:
            logging.info(f"Output: {completed_process.stdout.decode()}")
    except CalledProcessError as e:
        logging.error(f"An error occurred: {e}")

def package_manager(distro, packages, action, verbose, dry_run):

    if distro in {"debian", "ubuntu"} and not dry_run:
        run(["sudo", "apt", "update"], capture_output=False)

    for package in packages:
        name = package.get("name", "")
        check_value = package.get("check_value", "")
        package_type = package.get("type", "")
        check_script = package.get("check_script", [])

        try:
            os.makedirs(path.join(CACHE_PATH), exist_ok=True)
            original_dir = getcwd()
            chdir(path.join(CACHE_PATH))

            if package_type in {
                "package",
                "url-package",
                "local-package",
                "AUR-package",
            }:
                handle_standard_package(
                    distro, package, check_value, action, dry_run, verbose
                )
            elif package_type == "special-package":
                special_package_installer(
                    package, check_script, action, dry_run, verbose
                )
            elif package_type == "remove-package":
                handle_removable_package(
                    distro, package, check_value, action, dry_run, verbose
                )
            elif package_type in ["get-keys"]:
                handle_repo_keys(
                    distro, package, check_script, action, dry_run, verbose
                )
            elif package_type in {"service", "group"}:
                handle_service_or_group(distro, package, action, dry_run, verbose)
            elif package_type == "package-flatpak":
                handle_flatpak_package(package, check_value, action, dry_run, verbose)
        except CalledProcessError as e:
            handle_error(e, check_value, action, name, dry_run, package, verbose)

        finally:
            chdir(original_dir)


def handle_standard_package(distro, package, check_value, action, dry_run, verbose):
    """
    Handles installation or removal of standard packages based on the target distro.

    Args:
        distro (str): The target Linux distribution.
        package (dict): Package metadata.
        check_value (str): The name(s) of the package(s) to check.
        action (str): Action to perform ('install' or 'remove').
        dry_run (bool): If True, only simulate actions.
        verbose (file-like): If True, suppress verbose.
    """
    check_values = (
        check_value.split()
    )  # Split the package names for individual checking
    not_installed = []
    installed = []

    for value in check_values:
        if distro == "arch":
            result = run(["pacman", "-Q", value], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        elif distro in {"debian", "ubuntu"}:
            result = run(
                ["apt", "list", "--installed", value], stdout=PIPE, stderr=PIPE, stdin=PIPE
            )
        elif distro == "fedora":
            result = run(
                ["dnf", "list", "--installed", value], stdout=PIPE, stderr=PIPE, stdin=PIPE
            )

        verbose = result.stdout.decode("utf-8").lower()
        if value.lower() in verbose:
            installed.append(value)
        else:
            not_installed.append(value)

    # Handle action logic
    if action == "install":
        if not_installed:
            logging.info(f"Installing {package['name']}...")
            logging.debug(
                f"Installing the following packages: {', '.join(not_installed)}"
            )
            if not dry_run:
                package_installer(distro, package, verbose)
        else:
            logging.info(f"No packages to install: {', '.join(installed)}")
    elif action == "remove":
        if installed:
            logging.info(f"Removing {package['name']}...")
            if not dry_run:
                package_remover(distro, package, verbose)
        else:
            logging.info(f"No packages to remove: {', '.join(not_installed)}")


def handle_removable_package(distro, package, check_value, action, dry_run, verbose):
    if distro == "arch":
        result = run(["pacman", "-Q"] + check_value.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    elif distro in {"debian", "ubuntu"}:
        result = run(
            ["apt", "list", "--installed"] + check_value.split(),
            stdout=PIPE,
            stderr=PIPE, stdin=PIPE,
        )
    elif distro == "fedora":
        result = run(
            ["dnf", "list", "installed"] + check_value.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE
        )

    if "error" not in result.stderr.decode("utf-8").lower():
        if action == "install":
            logging.info(f"{package['name']} not installed. Installing...")
            if not dry_run:
                package_remover(distro, package, verbose)
        elif action == "remove":
            logging.info(f"{package['name']} not installed. Skipping...")


def handle_repo_keys(distro, package, check_script, action, dry_run, verbose):
    for script in check_script:
        if not script:
            logging.warning("No script provided to check the repo key. Skipping...")
            continue

        if (path.exists(script) or path.dirname(script)):
            if action == "install":
                logging.info(f"{package['name']} repo key installed. Skipping...")
            elif action == "remove":
                logging.info(f"{package['name']} repo key removing...")
                if not dry_run:
                    package_remover(distro, package, verbose)
        else:
            if action == "install":
                logging.info(f"{package['name']} repo key not installed. Installing...")
                if not dry_run:
                    package_installer(distro, package, verbose)
            elif action == "remove":
                logging.info(f"{package['name']} repo key not installed. Skipping...")


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
        if (path.exists(script) or path.dirname(script)) and script != "":
            script_executed = True
            break

    try:
        if action == "install":
            logging.info(f"Installing {app_name}...")

            if script_executed:
                logging.info("App already installed. Skipping...")
                return

            # Replace placeholders with values dynamically
            for special_value in special_values:
                for key, value in special_value.items():
                    install_script = [
                        cmd.replace(f"${key}", value) for cmd in install_script
                    ]

            # Replace $CACHE_PATH explicitly
            install_script = [
                cmd.replace("$CACHE_PATH", CACHE_PATH) for cmd in install_script
            ]

            # Execute install scripts
            for command in install_script:
                if dry_run:
                    logging.debug(f"Would execute: {command}")
                else:
                    run_command(command, verbose)

            logging.info(f"{app_name} installation completed.")

        elif action == "remove":
            logging.info(f"Removing {app_name}...")

            if not script_executed:
                logging.info("App not installed. Skipping...")
                return

            for special_value in special_values:
                for key, value in special_value.items():
                    remove_script = [
                        cmd.replace(f"${key}", value) for cmd in remove_script
                    ]

            # Replace $CACHE_PATH in remove scripts
            remove_script = [
                cmd.replace("$CACHE_PATH", CACHE_PATH) for cmd in remove_script
            ]

            # Execute remove scripts
            for command in remove_script:
                if dry_run:
                    logging.debug(f"Would execute: {command}")
                else:
                    run_command(command, verbose)

            logging.info(f"{app_name} removal completed.")
    except Exception as e:
        logging.error(f"An error occurred while handling {app_name}: {e}")


def handle_service_or_group(distro, package, action, dry_run, verbose):
    if action == "install":
        logging.info(f"Installing {package['name']} service/group...")
        if not dry_run:
            package_installer(distro, package, verbose)
    elif action == "remove":
        logging.info(f"skip removing {package['name']} service/group...")


def handle_flatpak_package(package, check_value, action, dry_run, verbose):
    result = run(["flatpak", "list"], stdout=PIPE, stderr=PIPE, stdin=PIPE)

    if check_value not in result.stdout.decode("utf-8"):
        if action == "install":
            logging.info(f"{package['name']} not installed. Installing...")
            if not dry_run:
                package_installer("fedora", package, verbose)
        elif action == "remove":
            logging.info(f"No {package['name']} to remove. Skipping...")
    else:
        if action == "install":
            logging.info(f"{package['name']} already installed. Skipping...")
        elif action == "remove":
            logging.info(f"Removing {package['name']}...")
            if not dry_run:
                package_remover("fedora", package, verbose)


def handle_error(e, check_value, action, name, dry_run, package, verbose):
    error_message = e.stderr.decode("utf-8").lower()
    if check_value not in error_message:
        if action == "install":
            logging.info(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer("fedora", package, verbose)
        elif action == "remove":
            logging.info(f"No {name} to remove. Skipping...")
    else:
        logging.error(f"An error occurred while handling {name}: {e}")

def service_installer(service, action, verbose):
    try:
        if action == "install":
            run_command(f"sudo systemctl restart {service}", verbose)
            run_command(f"sudo systemctl enable {service}", verbose)
        elif action == "remove":
            run_command(f"sudo systemctl stop {service}", verbose)
            run_command(f"sudo systemctl disable {service}", verbose)
    except CalledProcessError as err:
        logging.error(f"An error occurred: {err}")


def package_installer(distro, package, verbose):
    current_user = getenv("USER")
    package_type = package.get("type", "")
    install_value = package.get("install_value", "")

    try:
        if distro == "arch":
            if package_type == "package":
                run_command(f"sudo pacman -S {install_value} --noconfirm", verbose)
            elif package_type == "local-package":
                handle_local_package(install_value, distro, CACHE_PATH, verbose)
            elif package_type == "service":
                run_command(f"sudo systemctl restart {install_value}", verbose)
                run_command(f"sudo systemctl enable {install_value}", verbose)
            elif package_type == "group":
                run_command(f"sudo usermod -aG {install_value} {current_user}", verbose)
            elif package_type == "repo-flathub":
                run_command(
                    f"sudo flatpak remote-add --if-not-exists flathub {install_value}",
                    verbose,
                )
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak install -y {install_value}", verbose)
            elif package_type == "AUR-package":
                handle_aur_package(install_value, CACHE_PATH, verbose)

        elif distro in {"debian", "ubuntu"}:
            if package_type == "package":
                run_command(f"sudo apt install -y {install_value}", verbose)
            elif package_type in ["get-keys", "special-package"]:
                for command in package.get("install_script", []):
                    run_command(command, verbose)
            elif package_type == "local-package":
                handle_local_package(install_value, distro, CACHE_PATH, verbose)
            elif package_type == "service":
                run_command(f"sudo systemctl restart {install_value}", verbose)
                run_command(f"sudo systemctl enable {install_value}", verbose)
            elif package_type == "group":
                run_command(f"sudo usermod -aG {install_value} {current_user}", verbose)
            elif package_type == "repo-flathub":
                run_command(
                    f"sudo flatpak remote-add --if-not-exists flathub {install_value}",
                    verbose,
                )
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak install -y {install_value}", verbose)

        elif distro == "fedora":
            if package_type == "package":
                run_command(f"sudo dnf install -y {install_value}", verbose)
            elif package_type in ["get-keys", "special-package"]:
                for command in package.get("install_script", []):
                    run_command(command, verbose)
            elif package_type == "url-package":
                install_value = replace_fedora_version(install_value)
                run_command(f"sudo dnf install -y {install_value}", verbose)
            elif package_type == "local-package":
                handle_local_package(install_value, distro, CACHE_PATH, verbose)
            elif package_type == "service":
                run_command(f"sudo systemctl restart {install_value}", verbose)
                run_command(f"sudo systemctl enable {install_value}", verbose)
            elif package_type == "group":
                run_command(f"sudo usermod -aG {install_value} {current_user}", verbose)
            elif package_type == "repo-flathub":
                run_command(
                    f"sudo flatpak remote-add --if-not-exists flathub {install_value}",
                    verbose,
                )
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak install -y {install_value}", verbose)

    except CalledProcessError as err:
        logging.error(f"An error occurred: {err}")


def package_remover(distro, package, verbose):
    package_type = package.get("type", "")
    remove_value = package.get("remove_value", "")

    try:
        if distro == "arch":
            if package_type in {"package", "AUR-package", "local-package"}:
                run_command(f"sudo pacman -R {remove_value} --noconfirm", verbose)
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak remove -y {remove_value}", verbose)

        elif distro in {"debian", "ubuntu"}:
            if package_type in {
                "package",
                "url-package",
                "local-package",
                "remove-package",
            }:
                run_command(f"sudo apt remove -y {remove_value}", verbose)
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak remove -y {remove_value}", verbose)
            elif package_type in ["get-keys", "special-package"]:
                for command in package.get("remove_script", []):
                    run_command(command, verbose)

        elif distro == "fedora":
            if package_type in {
                "package",
                "url-package",
                "local-package",
                "remove-package",
            }:
                run_command(f"sudo dnf remove -y {remove_value}", verbose)
            elif package_type == "package-flatpak":
                run_command(f"sudo flatpak remove -y {remove_value}", verbose)
            elif package_type in ["get-keys", "special-package"]:
                for command in package.get("remove_script", []):
                    run_command(command, verbose)

    except CalledProcessError as err:
        logging.error(f"An error occurred: {err}")


def handle_local_package(install_value, distro, CACHE_PATH, verbose):
    package_types = {
        "arch": "tar.gz",
        "debian": "deb",
        "ubuntu": "deb",
        "fedora": "rpm",
    }

    if distro not in package_types:
        raise ValueError(f"Unsupported distribution: {distro}")

    package_type = package_types[distro]
    local_path = path.join(CACHE_PATH, f"local.package.{package_type}")

    try:
        run(
            ["wget", "--progress=bar:force", "-O", local_path, install_value],
            cwd=CACHE_PATH,
            stderr=verbose,
            stdout=verbose,
            check=True,
        )

        if distro == "arch":
            run(
                ["sudo", "pacman", "-U", local_path, "--noconfirm"],
                cwd=CACHE_PATH,
                stderr=verbose,
                stdout=verbose,
                check=True,
            )
        elif distro in {"debian", "ubuntu"}:
            run(
                ["sudo", "dpkg", "-i", local_path],
                stderr=verbose,
                stdout=verbose,
                check=True,
            )
            run(
                ["sudo", "apt", "--fix-broken", "install", "-y"],
                stderr=verbose,
                stdout=verbose,
                check=True,
            )
        elif distro == "fedora":
            run(
                ["sudo", "dnf", "install", "-y", local_path],
                stderr=verbose,
                stdout=verbose,
                check=True,
            )
    except CalledProcessError as err:
        logging.error(f"An error occurred: {err}")
    finally:
        if path.exists(local_path):
            run(
                ["sudo", "rm", "-f", local_path],
                cwd=CACHE_PATH,
                stderr=verbose,
                stdout=verbose,
            )


def handle_aur_package(install_value, CACHE_PATH, verbose):
    repository_directory = f"{CACHE_PATH}/{install_value}"
    run(
        ["git", "clone", f"https://aur.archlinux.org/{install_value}.git"],
        cwd=CACHE_PATH,
    )
    sleep(10)
    run(
        ["makepkg", "-si", "--noconfirm"],
        cwd=repository_directory,
        stderr=verbose,
        stdout=verbose,
    )
    sleep(10)
    run(
        ["sudo", "rm", "-rf", install_value],
        cwd=CACHE_PATH,
        stderr=verbose,
        stdout=verbose,
    )


def replace_fedora_version(value):
    fedora_version = check_output(["rpm", "-E", "%fedora"], text=True).strip()
    return value.replace("$(rpm -E %fedora)", fedora_version)
