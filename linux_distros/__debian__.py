from os import getenv
import subprocess


def debian_package_installer(packages, hide_output):
    subprocess.run(["apt", "update"])
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.run(["apt", "list", "installed", value])
            elif type == "install-package-flatpak":
                subprocess.run(["flatpak", "list", "|", "grep", value])
            else:
                type_of_action(data, hide_output)
        except subprocess.CalledProcessError:
            type_of_action(data, hide_output)


def type_of_action(data, hide_output):

    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    name = data.get("name", "")
    type = data.get("type", "")
    value = data.get("value", "")
    try:
        if hide_output:
            devnull = open("/dev/null", "w")
            stdout = stderr = devnull
        else:
            stdout = stderr = None

        if type == "install-package":
            packages_to_install = value.split()  # Split the package names into a list
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + packages_to_install,
                check=True,
                stderr=stderr,
                stdout=stdout,
            )

        elif type == "get-keys":
            keys = data["script"]
            for command in keys:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=stderr, stdout=stdout
                    )
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
                stderr=stderr,
                stdout=stdout,
            )

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package names into a list
            subprocess.run(
                ["sudo", "apt", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=stderr,
                stdout=stdout,
            )

        elif type == "install-service":
            subprocess.run(["sudo", "systemctl", "restart", value])
            subprocess.run(["sudo", "systemctl", "enable", value])

        elif type == "add-group":
            subprocess.run(["sudo", "usermod", "-aG", value, current_user])

        elif type == "add-repo-flathub":
            print(f"\n{name} repo adding to flatpak")
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value],
                check=True,
            )

        elif type == "install-package-flatpak":
            print(f"\n{name} flatpak Package(s) insalling")
            subprocess.run(
                ["sudo", "flatpak", "install", "-y", value],
                check=True,
                stderr=stderr,
                stdout=stdout,
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
