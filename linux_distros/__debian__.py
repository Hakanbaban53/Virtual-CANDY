from os import getenv
import os
import subprocess


def debian_package_installer(packages):
    subprocess.call(["sudo", "apt", "update"])
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.call(["sudo", "apt", "list", "installed", value])
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
    name = data.get("name", "")
    try:
        if type == "install-package":
            packages_to_install = value.split()  # Split the package names into a list
            subprocess.call(["sudo", "apt", "install"] + packages_to_install)

        elif type == "get-keys":
            try:
                script = """
                    sudo apt-get install ca-certificates curl
                    sudo install -m 0755 -d /etc/apt/keyrings
                    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
                    sudo chmod a+r /etc/apt/keyrings/docker.asc

                    # Add the repository to Apt sources:
                    echo \
                    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
                    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                    sudo apt-get update
                """
                os.system(script)
                print("Docker repository keys installed successfully.")
            except subprocess.CalledProcessError as err:
                print(f"An error occurred: {err}")

        elif type == "local-package":
            subprocess.run(
                [
                    "wget",
                    "--show-progress",
                    "--progress=bar:force",
                    "-O",
                    f"{target_directory}local.package.deb",
                    value,
                ],
                check=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "--fix-broken",
                    "install",
                    f"{target_directory}local.package.deb",
                ],
                check=True,
            )

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package names into a list
            subprocess.call(["sudo", "apt", "remove"] + packages_to_remove)

        elif type == "add-repo-flathub":
            subprocess.call(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", value]
            )

        elif type == "install-service":
            subprocess.call(["sudo", "systemctl", "restart", value])
            subprocess.call(["sudo", "systemctl", "enable", value])

        elif type == "add-group":
            subprocess.call(["sudo", "usermod", "-aG", value, current_user])

        elif type == "install-package-flatpak":
            subprocess.call(["sudo", "flatpak", "install", "-y", value])

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
