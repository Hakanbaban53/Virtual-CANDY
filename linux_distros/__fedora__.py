from os import getenv
import subprocess


def fedora_package_installer(packages):
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.call(["sudo", "dnf", "list", "installed", value])
            elif type == "install-package-flatpak":
                subprocess.call(["flatpak", "list", "|", "grep", value])
            else:
                type_of_action(data)
        except subprocess.CalledProcessError:
            type_of_action(data)


def type_of_action(data):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    type = data.get("type", "")
    value = data.get("value", "")
    try:
        if type == "install-package":
            packages_to_install = value.split()
            subprocess.call(
                ["sudo", "dnf", "install", "-y"] + packages_to_install
            )

        elif type == "install-url-package":
            fedora_version = subprocess.check_output(
                ["rpm", "-E", "%fedora"], text=True
            ).strip()
            value = value.replace("$(rpm -E %fedora)", fedora_version)
            subprocess.call(["sudo", "dnf", "install", value])

        elif type == "local-package":
            subprocess.run(
                [
                    "wget",
                    "--show-progress",
                    "--progress=bar:force",
                    "-O",
                    "local.package.rpm",
                    value,
                ],
                cwd=target_directory,
                check=True,
            )
            subprocess.run(
                ["sudo", "dnf", "install", "-y", f"local.package.rpm"],
                cwd=target_directory,
                check=True,
            )

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package types into a list
            subprocess.call(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove
            )

        elif type == "config-manager":
            subprocess.call(
                ["sudo", "dnf", "config-manager", "--add-repo", value]
            )

        elif type == "install-service":
            print(f"\n{type}  service installing...")
            subprocess.call(["sudo", "systemctl", "restart", value])
            subprocess.call(["sudo", "systemctl", "enable", value])

        elif type == "add-group":
            subprocess.call(["sudo", "usermod", "-aG", value, current_user])

        elif type == "add-repo-flathub":
            subprocess.call(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", value]
            )

        elif type == "install-package-flatpak":
            subprocess.call(["sudo", "flatpak", "install", "-y", value])

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
