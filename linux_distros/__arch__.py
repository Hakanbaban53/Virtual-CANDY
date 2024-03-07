from os import getenv
import subprocess


def arch_package_manager(packages, hide_output):
    if hide_output:
        devnull = open("/dev/null", "w")
        hide = devnull
    else:
        hide = None

    for data in packages:
        value = data.get("value", "")
        type = data.get("type", "")

        try:
            if type == "install-package":
                packages_to_check = value.split()
                result = subprocess.run(
                    ["pacman", "-Q"] + packages_to_check,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Check if the package is not installed based on the error message
                if "error" in result.stderr.decode("utf-8"):
                    print(packages_to_check, "not installed. Installing...")
                    installer(data, hide)
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
                    installer(data, hide)

                else:
                    print(value, "was installed. Skipping...")

            else:
                installer(data, hide)

        except subprocess.CalledProcessError:
            installer(data, hide)


def installer(data, hide):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    name = data.get("name", "")
    type = data.get("type", "")
    value = data.get("value", "")
    try:
        if type == "install-package":
            subprocess.run(
                ["sudo", "pacman", "-S", value, "--noconfirm"],
                check=True,
                stderr=hide,
                stdout=hide,
            )

        elif type == "local-package":
            subprocess.run(
                [
                    "wget",
                    "--show-progress",
                    "--progress=bar:force",
                    "-O",
                    f"{target_directory}package.pkg.tar.zst",
                    value,
                ],
                cwd=target_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )
            subprocess.run(
                [
                    "sudo",
                    "pacman",
                    "-U",
                    f"{target_directory}package.pkg.tar.zst",
                    "--noconfirm",
                ],
                cwd=target_directory,
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
            subprocess.run(
                ["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", value]
            )

        elif type == "install-package-flatpak":
            subprocess.run(["sudo", "flatpak", "install", "-y", value])

        elif type == "install-package-AUR-git":
            repository_directory = f"{target_directory}/{value}"
            subprocess.run(
                ["git", "clone", f"https://aur.archlinux.org/{value}.git"],
                cwd=target_directory,
            )
            subprocess.run(
                ["makepkg", "-si", "--noconfirm"],
                cwd=repository_directory,
                check=True,
                stderr=hide,
                stdout=hide,
            )
            subprocess.run(["makepkg", "--clean"], cwd=repository_directory)

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")

def remover():
    print("Remover Working.")