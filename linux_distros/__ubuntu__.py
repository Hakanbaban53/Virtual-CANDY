from os import getenv
import subprocess


def ubuntu_package_installer(packages, hide_output):
    if hide_output:
        devnull = open("/dev/null", "w")
        hide = devnull
    else:
        hide = None

    subprocess.run(["sudo", "apt", "update"])

    for data in packages:
        value = data.get("value", "")
        type = data.get("type", "")

        try:
            if type == "install-package":
                packages_to_check = value.split()
                result = subprocess.run(
                    ["apt", "list", "--installed"] + packages_to_check,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Check if any of the packages is not installed based on the output
                not_installed_packages = [
                    package for package in packages_to_check if package not in result.stdout.decode("utf-8")
                ]

                if not_installed_packages:
                    print(not_installed_packages, "not installed. Installing...")
                    type_of_action(data, hide)
                else:
                    print(packages_to_check, "was installed. Skipping...")

            elif type == "install-package-flatpak":
                result = subprocess.run(
                    ["flatpak", "list"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Check if the value is not in the output
                if value not in result.stdout.decode("utf-8"):
                    print(value, "not installed. Installing...")
                    type_of_action(data, hide)

                else:
                    print(value, "was installed. Skipping...")

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
            packages_to_install = value.split()  # Split the package names into a list
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + packages_to_install,
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif type == "get-keys":
            keys = data["script"]
            for command in keys:
                try:
                    subprocess.run(
                        command, shell=True, check=True, stderr=hide, stdout=hide
                    )
                    print("Script executed successfully.")
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
                    "-y",
                    f"{target_directory}local.package.deb",
                ],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package names into a list
            subprocess.run(
                ["sudo", "apt", "remove", "-y"] + packages_to_remove,
                check=True,
                stderr=hide,
                stdout=hide,
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
                stderr=hide,
                stdout=hide,
            )

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
