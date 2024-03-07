from os import getenv
import subprocess
from time import sleep


def fedora_package_manager(packages, hide_output, action):
    if hide_output:
        devnull = open("/dev/null", "w")
        hide = devnull
    else:
        hide = None

        for data in packages:
            value = data.get("value", "")
            package_type = data.get("type", "")

            try:
                if package_type == "install-package":
                    packages_to_check = value.split()
                    result = subprocess.run(
                        ["dnf", "list", "installed"] + packages_to_check,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                    )

                    # Check if the package is not installed based on the error message
                    if "error" in result.stderr.decode("utf-8").lower():
                        print(packages_to_check, "not installed. Installing...")
                        package_installer(data, hide)

                    else:
                        print(packages_to_check, "was installed. Skipping...")

                elif package_type == "install-package-flatpak":
                    result = subprocess.run(
                        ["flatpak", "list"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                    )

                    # Check if the value is not in the output
                    if value not in result.stdout.decode("utf-8"):
                        print(packages_to_check, "not installed. Installing...")
                        package_installer(data, hide)

                    else:
                        print(packages_to_check, "was installed. Skipping...")

                else:
                    package_installer(data, hide)

            except subprocess.CalledProcessError:
                package_installer(data, hide)


def package_installer(data, hide):

    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    name = data.get("name", "")
    package_type = data.get("type", "")
    value = data.get("value", "")

    try:
        if package_type == "install-package":
            print(f"\n{name} Package(s) insalling")
            packages_to_install = value.split()
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + packages_to_install,
                check=True,
                stderr=hide,
                stdout=hide,
            )
            sleep(10)
        elif package_type == "get-keys":
            keys = data["script"]
            for command in keys:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=hide, stdout=hide
                    )
                except subprocess.CalledProcessError as err:
                    print(f"An error occurred: {err}")

        elif package_type == "install-url-package":
            print(f"\n{name} Package(s) insalling")
            fedora_version = subprocess.check_output(
                ["rpm", "-E", "%fedora"], text=True
            ).strip()
            value = value.replace("$(rpm -E %fedora)", fedora_version)
            subprocess.run(
                ["sudo", "dnf", "install", "-y", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "local-package":
            print(f"\n{name} Package(s) insalling")
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
                stderr=hide,
                stdout=hide,
            )

            subprocess.run(
                ["sudo", "dnf", "install", "-y", f"local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

            subprocess.run(
                ["sudo", "rm", "-f", f"local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "remove-package":
            print(f"\n{name} Package(s) removing.")
            packages_to_remove = value.split()  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "config-manager":
            print(f"\n{name} repo adding.")
            subprocess.run(
                ["sudo", "dnf", "config-manager", "--add-repo", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "install-service":
            print(f"\n\n{name}  service installing...")
            subprocess.run(
                ["sudo", "systemctl", "restart", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )
            subprocess.run(
                ["sudo", "systemctl", "enable", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "add-group":
            print(f"\n{name} adding to group")
            subprocess.run(
                ["sudo", "usermod", "-aG", value, current_user],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "add-repo-flathub":
            print(f"\n{name} repo adding to flatpak")
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "install-package-flatpak":
            print(f"\n{name} flatpak Package(s) insalling")
            subprocess.run(
                ["sudo", "flatpak", "install", "-y", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")


def package_remover(data, hide):
    name = data.get("name", "")
    package_type = data.get("type", "")
    value = data.get("value", "")

    try:

        if package_type == "install-package":
            print(f"\n{name} Package(s) removing.")
            packages_to_remove = value.split()  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif package_type == "install-package-flatpak":
            print(f"\n{name} flatpak Package(s) removing")
            subprocess.run(
                ["sudo", "flatpak", "remove", "-y", value],
                check=True,
                stderr=hide,
                stdout=hide,
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
