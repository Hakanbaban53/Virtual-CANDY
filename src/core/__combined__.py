import logging
import os
from subprocess import run, CalledProcessError
from os import path, chdir, getcwd

from core.__command_handler__ import run_command
from core.__constants__ import CACHE_PATH
from core.__linux_system__ import systemd_service_installer, usermod_group_installer
from core.package_handlers.__flatpak__ import handle_flatpak_package, handle_flatpak_repo
from core.package_handlers.__normal__ import handle_standard_package
from core.package_handlers.__special__ import special_package_installer

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
                    distro, package, package_type, check_value, action, dry_run, verbose
                )
            elif package_type == "special-package":
                special_package_installer(
                    package, check_script, action, dry_run, verbose
                )
            elif package_type == "remove-package":
                handle_standard_package(
                    distro, package, check_value, "remove", dry_run, verbose
                )
            elif package_type in ["run-command"]:
                run_basic_command(
                    distro, package, check_script, action, dry_run, verbose
                )
            elif package_type in {"service"}:
                install_value = package.get("install_value", "")
                systemd_service_installer(install_value, action, verbose)
            elif package_type in {"group"}:
                install_value = package.get("install_value", "")
                usermod_group_installer(install_value, action, verbose)
            elif package_type == "repo-flathub":
                handle_flatpak_repo(package, dry_run, verbose)
            elif package_type == "package-flatpak":
                handle_flatpak_package(package, check_value, action, dry_run, verbose)
        except CalledProcessError as e:
            logging.error(e, check_value, action, name, dry_run, package, verbose)

        finally:
            chdir(original_dir)

def run_basic_command(package, check_script, action, dry_run, verbose):
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
                        for remove_script in package.get("remove_script", []):
                            run_command(command=remove_script, verbose=verbose)
        else:
            if action == "install":
                logging.info(f"{package['name']} repo key not installed. Installing...")
                if not dry_run:
                    for install_script in package.get("install_script", []):
                        run_command(command=install_script, verbose=verbose)
            elif action == "remove":
                logging.info(f"{package['name']} repo key not installed. Skipping...")

