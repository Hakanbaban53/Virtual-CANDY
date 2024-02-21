from os import getenv
import subprocess


def debian_package_installer(packages):
    subprocess.run(["sudo", "apt", "update"])
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.run(["sudo", "apt", "list", "installed", value])
            elif type == "install-package-flatpak":
                subprocess.run(["flatpak", "list", "|", "grep", value])
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
            packages_to_install = value.split()  # Split the package names into a list
            subprocess.run(["sudo", "apt", "install", "-y"] + packages_to_install)

        elif type == "get-keys":
            keys = data["script"]
            for command in keys:
                try:
                    subprocess.run(command, shell=True, check=True)
                    print("Script executed successfully.")
                except subprocess.runedProcessError as err:
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
                    "-y",
                    f"{target_directory}local.package.deb",
                ],
                check=True,
            )

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package names into a list
            subprocess.run(["sudo", "apt", "remove", "-y"] + packages_to_remove)

        elif type == "install-service":
            subprocess.run(["sudo", "systemctl", "restart", value])
            subprocess.run(["sudo", "systemctl", "enable", value])

        elif type == "add-group":
            subprocess.run(["sudo", "usermod", "-aG", value, current_user])

        elif type == "install-package-flatpak":
            subprocess.run(["sudo", "flatpak", "install", "-y", value])

        elif type == "add-repo-flathub":
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value]
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
