from subprocess import run, PIPE, CalledProcessError
from os import devnull, getenv, path
from time import sleep


def arch_package_manager(packages, output, action, dry_run):
    hide = open(devnull, "w") if not output else None

    for package in packages:
        name = package.get("name", "")
        check_value = package.get("check_value", "")
        package_type = package.get("type", "")
        check_script = package.get("check_script", [])

        try:
            if package_type in {"package", "AUR-package", "local-package"}:
                handle_standard_package(check_value, name, action, dry_run, package, hide)

            elif package_type in {"service", "group"}:
                handle_service_or_group(name, action, dry_run, package, hide)

            elif package_type == "get-keys":
                handle_repo_keys(check_script, name, action, dry_run, package, hide)

            elif package_type == "package-flatpak":
                handle_flatpak_package(
                    check_value, name, action, dry_run, package, hide
                )

        except CalledProcessError as e:
            handle_error(e, name, action, package, dry_run, hide)


def handle_standard_package(check_value, name, action, dry_run, package, hide):
    packages_to_check = check_value.split()
    result = run(
        ["pacman", "-Q"] + packages_to_check, stdout=PIPE, stderr=PIPE, check=True
    )

    if "error" not in result.stderr.decode("utf-8").lower():
        if action == "install":
            print(f"{name} was installed. Skipping...")
        elif action == "remove":
            print(f"{name} removing...")
            if not dry_run:
                package_remover(package, hide)
    else:
        if action == "install":
            print(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} not installed. Skipping...")


def handle_service_or_group(name, action, dry_run, package, hide):
    if action == "install":
        print(f"{name} service/group (re)installing...")
        if not dry_run:
            package_installer(package, hide)
    elif action == "remove":
        print("Skipping the service/group...")


def handle_repo_keys(check_script, name, action, dry_run, package, hide):
    for path_keys in check_script:
        if not path_keys:
            if action == "install":
                print(f"{name} Installing...")
                if not dry_run:
                    package_installer(package, hide)
            elif action == "remove":
                print(f"{name} Skipping...")
        elif path.exists(path_keys):
            if action == "install":
                print(f"{name} repo key installed. Skipping...")
            elif action == "remove":
                print(f"{name} repo key removing...")
                if not dry_run:
                    package_remover(package, hide)
        else:
            if action == "install":
                print(f"{name} repo key not installed. Installing...")
                if not dry_run:
                    package_installer(package, hide)
            elif action == "remove":
                print(f"{name} repo key not installed. Skipping...")


def handle_flatpak_package(check_value, name, action, dry_run, package, hide):
    result = run(["flatpak", "list"], stdout=PIPE, stderr=PIPE, check=True)

    if check_value not in result.stdout.decode("utf-8"):
        if action == "install":
            print(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} Not installed. Skipping...")
    else:
        if action == "install":
            print(f"{name} was installed. Skipping...")
        elif action == "remove":
            print(f"{name} removing...")
            if not dry_run:
                package_remover(package, hide)


def handle_error(e, name, action, package, dry_run, hide):
    error_message = e.stderr.decode("utf-8").lower()

    if "error" in error_message:
        if action == "install":
            print(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer(package, hide)
        elif action == "remove":
            print(f"{name} Not installed. Skipping...")
    else:
        print(f"An error occurred: {e}")


def package_installer(package, hide):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    package_type = package.get("type", "")
    install_value = package.get("install_value", "")

    try:
        if package_type == "package":
            run(
                ["sudo", "pacman", "-S", install_value, "--noconfirm"],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "local-package":
            local_package_installer(install_value, target_directory, hide)

        elif package_type == "service":
            run(
                ["sudo", "systemctl", "restart", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )
            run(
                ["sudo", "systemctl", "enable", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "group":
            run(
                ["sudo", "usermod", "-aG", install_value, current_user],
                check=True,
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
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "package-flatpak":
            run(
                ["sudo", "flatpak", "install", "-y", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "AUR-package":
            handle_aur_package(install_value, target_directory, hide)

    except CalledProcessError as err:
        print(f"An error occurred: {err}")
        sleep(10)



def local_package_installer(install_value, target_directory, hide):
    run(
        [
            "wget",
            "--progress=bar:force",
            "-O",
            "local.package.pkg.tar.zst",
            install_value,
        ],
        cwd=target_directory,
        check=True,
        stderr=hide,
        stdout=hide,
    )
    run(
        ["sudo", "pacman", "-U", "local.package.pkg.tar.zst", "--noconfirm"],
        cwd=target_directory,
        check=True,
        stderr=hide,
        stdout=hide,
    )
    run(
        ["sudo", "rm", "-f", "local.package.pkg.tar.zst"],
        cwd=target_directory,
        check=True,
        stderr=hide,
        stdout=hide,
    )


def handle_aur_package(install_value, target_directory, hide):
    repository_directory = f"{target_directory}/{install_value}"
    run(
        ["git", "clone", f"https://aur.archlinux.org/{install_value}.git"],
        cwd=target_directory,
    )
    sleep(10)
    run(
        ["makepkg", "-si", "--noconfirm"],
        cwd=repository_directory,
        check=True,
        stderr=hide,
        stdout=hide,
    )
    sleep(10)
    run(
        ["sudo", "rm", "-rf", install_value],
        cwd=target_directory,
        check=True,
        stderr=hide,
        stdout=hide,
    )



def package_remover(package, hide):
    package_type = package.get("type", "")
    remove_value = package.get("remove_value", "")

    try:
        if package_type in {"package", "AUR-package", "local-package"}:
            run(
                ["sudo", "pacman", "-R", remove_value, "--noconfirm"],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "package-flatpak":
            run(
                ["sudo", "flatpak", "remove", "-y", remove_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

    except CalledProcessError as err:
        print(f"An error occurred: {err}")
