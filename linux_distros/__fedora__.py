from os import getenv
import subprocess


def fedora_package_installer(packages, hide_output):
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.run(["sudo", "dnf", "list", "installed", value])
            elif type == "install-package-flatpak":
                subprocess.run(["flatpak", "list", "|", "grep", value])
            else:
                type_of_action(data, hide_output)
        except subprocess.runedProcessError:
            type_of_action(data, hide_output)


def type_of_action(data, hide_output):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    name = data.get("name", "")
    type = data.get("type", "")
    value = data.get("value", "")
    try:
        if hide_output:
            devnull = open('/dev/null', 'w')
            stdout = stderr = devnull
        else:
            stdout = stderr = None
            
        if type == "install-package":
            print(f"{name} Package(s) insalling")
            packages_to_install = value.split()
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + packages_to_install,
                check=True,
                stderr=stderr,
            )

        elif type == "install-url-package":
            print(f"{name} Package(s) insalling")
            fedora_version = subprocess.check_output(
                ["rpm", "-E", "%fedora"], text=True
            ).strip()
            value = value.replace("$(rpm -E %fedora)", fedora_version)
            subprocess.run(
                ["sudo", "dnf", "install", value],
                check=True,
                stderr=stderr,
            )

        elif type == "local-package":
            print(f"{name} Package(s) insalling")
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
                stderr=stderr,
            )

        elif type == "remove-package":
            print(f"{name} Package(s) removing.")
            packages_to_remove = value.split()  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=stderr,
            )

        elif type == "config-manager":
            print(f"{name} repo adding.")
            subprocess.run(
                ["sudo", "dnf", "config-manager", "--add-repo", value], check=True
            )

        elif type == "install-service":
            print(f"\n{name}  service installing...")
            subprocess.run(["sudo", "systemctl", "restart", value], check=True)
            subprocess.run(["sudo", "systemctl", "enable", value], check=True)

        elif type == "add-group":
            print(f"{name} adding to group")
            subprocess.run(["sudo", "usermod", "-aG", value, current_user], check=True)

        elif type == "add-repo-flathub":
            print(f"{name} repo adding to flatpak")
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value],
                check=True,
            )

        elif type == "install-package-flatpak":
            print(f"{name} flatpak Package(s) insalling")
            subprocess.run(
                ["sudo", "flatpak", "install", "-y", value],
                check=True,
                stderr=stderr,
            )

    except subprocess.runedProcessError as err:
        print(f"An error occurred: {err}")
