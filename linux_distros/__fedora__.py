from subprocess import run, PIPE, CalledProcessError, check_output
from os import path, devnull, getenv
from functions.__special_install_selector__ import SelectSpecialInstaller


def fedora_package_manager(packages, hide_output, action):
    hide = open(devnull, "w") if hide_output else None

    for data in packages:
        name = data.get("name", "")
        check_value = data.get("check_value", "")
        package_type = data.get("type", "")
        check_script = data.get("check_script", [])

        try:
            if package_type in {"package", "url-package", "local-package"}:
                packages_to_check = check_value.split()
                result = run(
                    ["dnf", "list", "installed"] + packages_to_check,
                    stdout=PIPE,
                    stderr=PIPE,
                    check=True,
                )

                if check_value not in result.stderr.decode("utf-8").lower():
                    if action == "install":
                        print(f"{name} was installed. Skipping...")
                    elif action == "remove":
                        print(f"{name} removing...")
                        package_remover(data, hide)

            if package_type == "special-package":
                SelectSpecialInstaller(hide, action, data, "fedora")

            if package_type == "remove-package":
                packages_to_check = check_value.split()
                result = run(
                    ["dnf", "list", "installed"] + packages_to_check,
                    stdout=PIPE,
                    stderr=PIPE,
                    check=True,
                )

                if "error" not in result.stderr.decode("utf-8").lower():
                    if action == "install":
                        print(f"{name} removing...")
                        package_remover(data, hide)
                    elif action == "remove":
                        print(f"{name} not installed. Skipping...")

            elif package_type == "get-keys":
                for path_keys in check_script:
                    if path_keys == "":
                        if action == "install":
                            print(f"{name} Installing...")
                            package_installer(data, hide)
                        elif action == "remove":
                            print(f"{name} Skipping...")
                    elif not path_keys:
                        print("Skipping...")
                    elif path.exists(path_keys):
                        if action == "install":
                            print(f"{name} repo key installed. Skipping...")
                        elif action == "remove":
                            print(f"{name} repo key removing...")
                            package_remover(data, hide)
                    else:
                        if action == "install":
                            print(f"{name} repo key installed. Installing...")
                            package_installer(data, hide)
                        elif action == "remove":
                            print(f"{name} repo key not installed. Skipping...")

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

            if check_value not in error_message:
                if action == "install":
                    print(f"{name} not installed. Installing...")
                    package_installer(data, hide)
                elif action == "remove":
                    print(f"{name} Not installed. Skipping...")
            else:
                raise e


def package_installer(data, hide):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    package_type = data.get("type", "")
    install_value = data.get("install_value", "")

    try:
        if package_type == "package":
            packages_to_install = install_value.split()
            run(
                ["sudo", "dnf", "install", "-y"] + packages_to_install,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "get-keys":
            install_script = data.get("install_script", [])
            for command in install_script:
                try:
                    run(command, shell=True, check=True, stderr=hide, stdout=hide)
                except CalledProcessError as err:
                    print(f"An error occurred: {err}")

        elif package_type == "url-package":
            fedora_version = check_output(
                ["rpm", "-E", "%fedora"], text=True
            ).strip()
            install_value = install_value.replace("$(rpm -E %fedora)", fedora_version)
            run(
                ["sudo", "dnf", "install", "-y", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "local-package":
            run(
                [
                    "wget",
                    "--progress=bar:force",
                    "-O",
                    "local.package.rpm",
                    install_value,
                ],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

            run(
                ["sudo", "dnf", "install", "-y", "local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

            run(
                ["sudo", "rm", "-f", "local.package.rpm"],
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

    except CalledProcessError as err:
        print(f"An error occurred: {err}")


def package_remover(data, hide):
    package_type = data.get("type", "")
    remove_value = data.get("remove_value", "")

    try:
        if package_type in {"package", "url-package", "local-package", "remove-package"}:
            packages_to_remove = remove_value.split()
            run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
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

        elif package_type == "get-keys":
            remove_script = data.get("remove_script", [])
            for command in remove_script:
                try:
                    run(command, shell=True, check=True, stderr=hide, stdout=hide)
                except CalledProcessError as err:
                    print(f"An error occurred: {err}")

    except CalledProcessError as err:
        print(f"An error occurred: {err}")
