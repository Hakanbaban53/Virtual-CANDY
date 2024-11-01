from subprocess import run, PIPE, CalledProcessError
from os import path, devnull, getenv

from functions.__special_install_selector__ import SelectSpecialInstaller


def debian_package_manager(packages, output, action, dry_run):
    hide = open(devnull, "w") if not output else None

    # Update package list
    if not dry_run:
        run(["sudo", "apt", "update"], stderr=hide, stdout=hide)

    for package in packages:
        name = package.get("name", "")
        check_value = package.get("check_value", "")
        package_type = package.get("type", "")
        check_script = package.get("check_script", [])

        try:
            if package_type in {"package", "url-package", "local-package"}:
                handle_standard_package(package, action, dry_run, hide)
            elif package_type == "special-package":
                SelectSpecialInstaller(hide, action, package, "ubuntu", dry_run)
            elif package_type == "remove-package":
                handle_removable_package(package, action, dry_run, hide)
            elif package_type == "get-keys":
                handle_repo_keys(package, check_script, action, dry_run, hide)
            elif package_type in {"service", "group"}:
                handle_service_or_group(package, action, dry_run, hide)
            elif package_type == "package-flatpak":
                handle_flatpak_package(package, check_value, action, dry_run, hide)
        except CalledProcessError as e:
            handle_error(e, check_value, action, name, dry_run, package, hide)


def handle_standard_package(package, action, dry_run, hide):
    name = package.get("name", "")
    check_value = package.get("check_value", "")
    packages_to_check = check_value.split()

    result = run(
        ["apt", "list", "--installed"] + packages_to_check,
        stdout=PIPE,
        stderr=PIPE,
    )
    installed_packages = result.stdout.decode("utf-8")
    not_installed_packages = [
        package for package in packages_to_check if package not in installed_packages
    ]

    if not_installed_packages:
        if action == "install":
            print(
                f"{name} not installed. {'Would install...' if dry_run else 'Installing...'}"
            )
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} not installed. Skipping...")
    else:
        if action == "install":
            print(f"{name} already installed. Skipping...")
        elif action == "remove":
            print(f"{name} {'Would remove...' if dry_run else 'Removing...'}")
            if not dry_run:
                package_remover(package, hide)


def handle_removable_package(package, action, dry_run, hide):
    name = package.get("name", "")
    check_value = package.get("check_value", "")
    packages_to_check = check_value.split()

    result = run(
        ["apt", "list", "--installed"] + packages_to_check,
        stdout=PIPE,
        stderr=PIPE,
    )

    not_installed_packages = [
        package
        for package in packages_to_check
        if package not in result.stdout.decode("utf-8")
    ]

    if not_installed_packages:
        if action == "install":
            print(f"{name} {'Would remove...' if dry_run else 'Removing...'}")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} not installed. Skipping...")


def handle_repo_keys(package, check_script, action, dry_run, hide):
    for path_key in check_script:
        if not path_key:
            print("Skipping...")
            continue

        if path.exists(path_key):
            if action == "install":
                print(f"{package['name']} repo key installed. Skipping...")
            elif action == "remove":
                print(f"{package['name']} repo key removing...")
                if not dry_run:
                    package_remover(package, hide)
        else:
            if action == "install":
                print(f"{package['name']} repo key not installed. Installing...")
                if not dry_run:
                    package_installer(package, hide)
            elif action == "remove":
                print(f"{package['name']} repo key not installed. Skipping...")


def handle_service_or_group(package, action, dry_run, hide):
    name = package.get("name", "")
    if action == "install":
        print(
            f"{name} service/group {'Would (re)install...' if dry_run else '(re)installing...'}"
        )
        if not dry_run:
            package_installer(package, hide)
    elif action == "remove":
        print(f"Skipping the service/group removal...")


def handle_flatpak_package(package, check_value, action, dry_run, hide):
    result = run(["flatpak", "list"], stdout=PIPE, stderr=PIPE)

    if check_value not in result.stdout.decode("utf-8"):
        if action == "install":
            print(f"{package['name']} not installed. Installing...")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{package['name']} not installed. Skipping...")
    else:
        if action == "install":
            print(f"{package['name']} was installed. Skipping...")
        elif action == "remove":
            print(f"{package['name']} removing...")
            if not dry_run:
                package_remover(package, hide)


def handle_error(e, check_value, action, name, dry_run, package, hide):
    error_message = e.stderr.decode("utf-8").lower()
    if check_value not in error_message:
        if action == "install":
            print(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} not installed. Skipping...")
    else:
        print(f"An error occurred: {e}")


def package_installer(package, hide):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    package_type = package.get("type", "")
    install_value = package.get("install_value", "")

    try:
        if package_type == "package":
            packages_to_install = install_value.split()
            run(
                ["sudo", "apt", "install", "-y"] + packages_to_install,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "get-keys":
            install_script = package.get("install_script", [])
            for command in install_script:
                try:
                    run(command, shell=True, stderr=hide, stdout=hide)
                except CalledProcessError as err:
                    print(f"An error occurred: {err}")

        elif package_type == "local-package":
            handle_local_package(install_value, target_directory, hide)

        elif package_type == "service":
            run(
                ["sudo", "systemctl", "restart", install_value],
                stderr=hide,
                stdout=hide,
            )
            run(
                ["sudo", "systemctl", "enable", install_value],
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "group":
            run(
                ["sudo", "usermod", "-aG", install_value, current_user],
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "repo-flathub":
            run(
                [
                    "sudo",
                    "flatpak",
                    "remote-add",
                    "--if-not-exists",
                    "flathub",
                    install_value,
                ],
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "package-flatpak":
            run(
                ["sudo", "flatpak", "install", "-y", install_value],
                stderr=hide,
                stdout=hide,
            )

    except CalledProcessError as err:
        print(f"An error occurred while installing {package.get('name', '')}: {err}")

def package_remover(package, hide):
    package_type = package.get("type", "")
    remove_value = package.get("remove_value", "")

    try:
        if package_type in {
            "package",
            "url-package",
            "local-package",
            "remove-package",
        }:
            packages_to_remove = remove_value.split()
            run(
                ["sudo", "apt", "remove", "-y"] + packages_to_remove,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "package-flatpak":
            run(
                ["sudo", "flatpak", "remove", "-y", remove_value],
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "get-keys":
            remove_script = package.get("remove_script", [])
            for command in remove_script:
                try:
                    run(command, shell=True, stderr=hide, stdout=hide)
                except CalledProcessError as err:
                    print(
                        f"An error occurred while removing {package.get('name', '')}: {err}"
                    )

    except CalledProcessError as err:
        print(f"An error occurred while removing {package.get('name', '')}: {err}")


def handle_local_package(install_value, target_directory, hide):
    local_path = path.join(target_directory, "local.package.deb")
    run(
        ["wget", "--progress=bar:force", "-O", local_path, install_value],
    )
    run(
        ["sudo", "dpkg", "-i", local_path],
        stderr=hide,
        stdout=hide,
    )
    run(
        ["sudo", "apt", "--fix-broken", "install", "-y"],
        stderr=hide,
        stdout=hide,
    )
    run(
        ["sudo", "rm", "-f", local_path],
        stderr=hide,
        stdout=hide,
    )

