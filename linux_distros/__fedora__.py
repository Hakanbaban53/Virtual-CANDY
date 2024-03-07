from os import getenv, devnull
import os
import subprocess


def fedora_package_manager(packages, hide_output, action):
    hide = open(devnull, "w") if hide_output else None

    for data in packages:
        check_value = data.get("check_value", "")
        package_type = data.get("type", "")
        check_script = data.get("check_script", [])

        try:
            if (
                package_type == "package"
                or package_type == "url-package"
                or package_type == "local-package"
            ):
                packages_to_check = check_value.split()
                result = subprocess.run(
                    ["dnf", "list", "installed"] + packages_to_check,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                # Check if the package is not installed based on the error message
                if "error" not in result.stderr.decode("utf-8").lower():
                    if action == "install":
                        print(check_value, "was installed. Skipping...")
                    elif action == "remove":
                        print(check_value, "removing...")
                        package_remover(data, hide)

            elif package_type == "get-keys":
                for path_keys in check_script:
                    if path_keys == "":
                        print("Skipped...")
                    else:
                        if os.path.exists(path_keys):
                            if action == "install":
                                print(check_value, "repo key installed. Skipping...")
                            elif action == "remove":
                                print(check_value, " repo key removing...")
                                package_remover(data, hide)
                        else:
                            if action == "install":
                                print(check_value, "repo key installed. Installing...")
                                package_installer(data, hide)
                            elif action == "remove":
                                print(check_value, "repo key not installed. Skipping...")

            elif package_type == "package-flatpak":
                result = subprocess.run(
                    ["flatpak", "list"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Check if the value is not in the output
                if check_value not in result.stdout.decode("utf-8"):
                    if action == "install":
                        print(packages_to_check, "not installed. Installing...")
                        package_installer(data, hide)
                    elif action == "remove":
                        print(packages_to_check, "Not installed. Skipping...")

                else:
                    if action == "install":
                        print(packages_to_check, "was installed. Skipping...")
                    elif action == "remove":
                        print(packages_to_check, "removing...")
                        package_remover(data, hide)

        except subprocess.CalledProcessError as e:
                # An exception is raised if the command has a non-zero exit code
            error_message = e.stderr.decode("utf-8").lower()

            if "error" in error_message:
                if action == "install":
                    print(check_value, "not installed. Installing...")
                    package_installer(data, hide)
                elif action == "remove":
                    print(check_value, "Not installed. Skipping...")
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
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + packages_to_install,
                check=True,
                stderr=hide,
                stdout=hide,
            )
        elif package_type == "get-keys":
            install_script = data.get("install_script", [])
            for command in install_script:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=hide, stdout=hide
                    )
                except subprocess.CalledProcessError as err:
                    print(f"An error occurred: {err}")

        elif package_type == "url-package":
            fedora_version = subprocess.check_output(
                ["rpm", "-E", "%fedora"], text=True
            ).strip()
            install_value = install_value.replace("$(rpm -E %fedora)", fedora_version)
            subprocess.run(
                ["sudo", "dnf", "install", "-y", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "local-package":
            subprocess.run(
                [
                    "wget",
                    "--show-progress",
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

            subprocess.run(
                ["sudo", "dnf", "install", "-y", "local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

            subprocess.run(
                ["sudo", "rm", "-f", "local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "remove-package":
            packages_to_remove = (
                install_value.split()
            )  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "service":
            subprocess.run(
                ["sudo", "systemctl", "restart", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )
            subprocess.run(
                ["sudo", "systemctl", "enable", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "group":
            subprocess.run(
                ["sudo", "usermod", "-aG", install_value, current_user],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "repo-flathub":
            subprocess.run(
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
            subprocess.run(
                ["sudo", "flatpak", "install", "-y", install_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")


def package_remover(data, hide):
    name = data.get("name", "")
    package_type = data.get("type", "")
    remove_value = data.get("remove_value", "")

    try:

        if package_type == "package":
            packages_to_remove = remove_value.split()  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "package-flatpak":
            subprocess.run(
                ["sudo", "flatpak", "remove", "-y", remove_value],
                check=True,
                stderr=hide,
                stdout=hide,
            )
        elif package_type == "get-keys":
            remove_script = data.get("remove_script", [])
            for command in remove_script:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=hide, stdout=hide
                    )
                except subprocess.CalledProcessError as err:
                    print(f"An error occurred: {err}")

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
