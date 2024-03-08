import os
from subprocess import run, PIPE, CalledProcessError
from os.path import exists


def arch_package_manager(packages, hide_output, action):
    hide = open(os.devnull, "w") if hide_output else None

    for data in packages:
        name = data.get("name", "")
        check_value = data.get("check_value", "")
        package_type = data.get("type", "")

        try:
            if package_type in {"package", "AUR-package", "local-package"}:
                packages_to_check = check_value.split()
                result = run(
                    ["pacman", "-Q"] + packages_to_check,
                    stdout=PIPE,
                    stderr=PIPE,
                    check=True,
                )

                if "error" not in result.stderr.decode("utf-8").lower():
                    if action == "install":
                        print(f"{name} was installed. Skipping...")
                    elif action == "remove":
                        print(f"{name} removing...")
                        package_remover(data, hide)

            elif package_type in {"service", "group"}:
                if action == "install":
                    print(f"{name} service/group (re)instaling...")
                    package_installer(data, hide)
                elif action == "remove":
                    print("Skipping the service/group...")

            elif package_type == "package-flatpak":
                result = run(["flatpak", "list"], stdout=PIPE, stderr=PIPE, check=True)

                if check_value not in result.stdout.decode("utf-8"):
                    if action == "install":
                        print(f"{name} not installed. Installing...")
                        package_installer(data, hide)
                    elif action == "remove":
                        print(f"{name} Not installed. Skipping...")

                else:
                    if action == "install":
                        print(f"{name} was installed. Skipping...")
                    elif action == "remove":
                        print(f"{name} removing...")
                        package_remover(data, hide)

        except CalledProcessError as e:
            error_message = e.stderr.decode("utf-8").lower()

            if "error" in error_message:
                if action == "install":
                    print(f"{name} not installed. Installing...")
                    package_installer(data, hide)
                elif action == "remove":
                    print(f"{name} Not installed. Skipping...")
            else:
                raise e


def package_installer(data, hide):
    current_user = os.getenv("USER")
    target_directory = f"/home/{current_user}/"
    package_type = data.get("type", "")
    install_value = data.get("install_value", "")
    try:
        if package_type == "package":
            run(
                ["sudo", "pacman", "-S", install_value, "--noconfirm"],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif type == "local-package":
            run(
                [
                    "wget",
                    "--show-progress",
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
                [
                    "sudo",
                    "pacman",
                    "-U",
                    "local.package.pkg.tar.zst",
                    "--noconfirm",
                ],
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

        elif type == "install-package-AUR-git":
            repository_directory = f"{target_directory}/{install_value}"
            run(
                ["git", "clone", f"https://aur.archlinux.org/{install_value}.git"],
                cwd=target_directory,
            )
            run(
                ["makepkg", "-si", "--noconfirm"],
                cwd=repository_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )
            run(
                ["makepkg", "--clean"],
                cwd=repository_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

    except CalledProcessError as err:
        print(f"An error occurred: {err}")


def package_remover(data, hide):
    package_type = data.get("type", "")
    remove_value = data.get("remove_value", "")
    try:
        if package_type == "package":
            run(
                ["sudo", "pacman", "-S", remove_value, "--noconfirm"],
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
