from os import getenv
import subprocess


def fedora_package_installer(packages, hide_output):

    if hide_output:
        devnull = open('/dev/null', 'w')
        hide = devnull
        
    else:
        hide = None

    for data in packages:

        value = data.get("value", "")

        try:
            if type == "install-package":
                packages_to_check = value.split()
                subprocess.run(["dnf", "list", "installed", packages_to_check])

            elif type == "install-package-flatpak":
                subprocess.run(["flatpak", "list", "|", "grep", value])

            else:
                type_of_action(data, hide)


        except subprocess.CalledProcessError:
            type_of_action(data, hide)


def type_of_action(data, hide):
    
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    name = data.get("name", "")
    type = data.get("type", "")
    value = data.get("value", "")

    try:    
        if type == "install-package":
            print(f"\n{name} Package(s) insalling")
            packages_to_install = value.split()
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + packages_to_install,
                check=True,
                stderr=hide,
                stdout=hide
            )

        elif type == "get-keys":
            keys = data["script"]
            for command in keys:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=hide, stdout=hide
                    )
                except subprocess.CalledProcessError as err:
                    print(f"An error occurred: {err}")

        # elif type == "install-url-package":
        #     print(f"\n{name} Package(s) insalling")
        #     fedora_version = subprocess.check_output(
        #         ["rpm", "-E", "%fedora"], text=True
        #     ).strip()
        #     value = value.replace("$(rpm -E %fedora)", fedora_version)
        #     subprocess.run(
        #         ["sudo", "dnf", "install", value],
        #         check=True,
        #         stderr=hide,
        #         stdout=hide
        #     )

        elif type == "local-package":
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
                stdout=hide
            )
            subprocess.run(
                ["sudo", "dnf", "install", "-y", f"local.package.rpm"],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide
            )

        elif type == "remove-package":
            print(f"\n{name} Package(s) removing.")
            packages_to_remove = value.split()  # Split the package types into a list
            subprocess.run(
                ["sudo", "dnf", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide
            )

        elif type == "config-manager":
            print(f"\n{name} repo adding.")
            subprocess.run(
                ["sudo", "dnf", "config-manager", "--add-repo", value],
                check=True,
                stderr=hide,
                stdout=hide
            )

        elif type == "install-service":
            print(f"\n\n{name}  service installing...")
            subprocess.run(["sudo", "systemctl", "restart", value],
                check=True,
                stderr=hide,
                stdout=hide)
            subprocess.run(["sudo", "systemctl", "enable", value],
                check=True,
                stderr=hide,
                stdout=hide)

        elif type == "add-group":
            print(f"\n{name} adding to group")
            subprocess.run(["sudo", "usermod", "-aG", value, current_user],
                check=True,
                stderr=hide,
                stdout=hide)

        elif type == "add-repo-flathub":
            print(f"\n{name} repo adding to flatpak")
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value],
                check=True,
                stderr=hide,
                stdout=hide
            )

        elif type == "install-package-flatpak":
            print(f"\n{name} flatpak Package(s) insalling")
            subprocess.run(
                ["sudo", "flatpak", "install", "-y", value],
                check=True,
                stderr=hide,
                stdout=hide
            )

    except subprocess.CalledProcessError as err:

        print(f"An error occurred: {err}")

