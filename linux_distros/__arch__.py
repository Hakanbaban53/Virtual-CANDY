from os import getenv
import subprocess


def arch_package_installer(packages, hide_output):
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.run(["pacman", "-Q", value, "--noconfirm"])
            elif type_of_action == "install-package-flatpak":
                result = subprocess.run(
                    ["flatpak", "list"], capture_output=True, text=True
                )
                if value in result.stdout:
                    print(f"{value} is already installed.")
                else:
                    print(f"{value} is not installed. Installing now...")
                    type_of_action(data, hide_output)
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
            subprocess.run(
                ["pacman", "-S", value, "--noconfirm"],
                check=True,
                stderr=stderr,
                stdout=stdout,
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
                ]
            )
            subprocess.run(
                [
                    "sudo",
                    "pacman",
                    "-U",
                    f"{target_directory}package.pkg.tar.zst",
                    "--noconfirm",
                ],
                check=True,
                stderr=stderr,
                stdout=stdout,
            )

        elif type == "install-service":
            subprocess.run(["systemctl", "restart", value])
            subprocess.run(["systemctl", "enable", value])

        elif type == "add-group":
            subprocess.run(["usermod", "-aG", value, current_user])

        elif type == "add-repo-flathub":
            subprocess.run(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", value]
            )

        elif type == "install-package-flatpak":
            subprocess.run(["flatpak", "install", "-y", value])

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
                stderr=stderr,
                stdout=stdout,
            )
            subprocess.run(["makepkg", "--clean"], cwd=repository_directory)

    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")
