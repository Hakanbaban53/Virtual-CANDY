
from genericpath import exists
from logging import error
from subprocess import CalledProcessError
from os import makedirs, path, chdir, getcwd

from core.__command_handler__ import run_command
from core.__constants__ import CACHE_PATH
from core.__linux_system__ import systemd_service_installer, usermod_group_installer
from core.package_handlers.__flatpak__ import (
    handle_flatpak_package,
    handle_flatpak_repo,
)
from core.package_handlers.__normal__ import handle_standard_package
from core.package_handlers.__special__ import special_package_installer


def package_manager(distro, packages, action, verbose, dry_run):

    if exists("/etc/debian_version") and not dry_run:
        run_command("sudo apt-get update", False)

    for package in packages:
        name = package.get("name", "")
        check_value = package.get("check_value", "")
        package_type = package.get("type", "")
        check_script = package.get("check_script", [])

        try:
            makedirs(path.join(CACHE_PATH), exist_ok=True)
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
                    distro=distro,
                    package=package,
                    package_type=package_type,
                    check_value=check_value,
                    action="remove",
                    dry_run=dry_run,
                    verbose=verbose,
                )
            elif package_type in ["run-command"]:
                special_package_installer(package, check_script, action, dry_run, verbose)
            elif package_type in {"service"}:
                install_value = package.get("install_value", "")
                systemd_service_installer(install_value, action, dry_run, verbose)
            elif package_type in {"group"}:
                install_value = package.get("install_value", "")
                usermod_group_installer(install_value, action, dry_run, verbose)
            elif package_type == "repo-flathub":
                handle_flatpak_repo(package, dry_run, verbose)
            elif package_type == "package-flatpak":
                handle_flatpak_package(package, check_value, action, dry_run, verbose)
        except CalledProcessError as e:
            error(e, check_value, action, name, dry_run, package, verbose)

        finally:
            chdir(original_dir)