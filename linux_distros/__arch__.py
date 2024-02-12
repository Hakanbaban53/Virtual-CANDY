import subprocess


def arch_package_installer(packages):
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.run(["sudo", "pacman", "-Qi", value])
            elif type_of_action == "install-package-flatpak":
                result = subprocess.run(['flatpak', 'list'], capture_output=True, text=True)
                if value in result.stdout:
                    print(f"{value} is already installed.")
                else:
                    print(f"{value} is not installed. Installing now...")
                    type_of_action(data)
            else:
                type_of_action(data)
        except subprocess.CalledProcessError:
            type_of_action(data)



def type_of_action(packages):
    for data in packages:
        type = data.get("type","")
        value = data.get("value","")
        try:
            if type == "install-package":
                subprocess.run(["sudo", "pacman", "-S", value])
            elif type== "local-package":
                subprocess.run(['wget', '--show-progress', '--progress=bar:force', '-O', 'package.pkg.tar.zst', value])
                subprocess.run(['sudo', 'pacman', '-U', 'package.pkg.tar.zst'])
            elif type == "install-service":
                subprocess.run(['sudo', 'systemctl', 'restart', value])
                subprocess.run(['sudo', 'systemctl', 'enable', value])
            elif type == "add-group":
                subprocess.run(['sudo', 'usermod', '-aG', value, '$USER'])
            elif type == "install-package-flatpak":
                subprocess.run(['flatpak', 'install', '-y', value])
            elif type == "install-package-AUR-git":
                subprocess.run(['git', 'clone', f'https://aur.archlinux.org/{value}.git'])
                subprocess.run(['cd', value])
                subprocess.run(['makepkg', '-si'])
                subprocess.run(['makepkg', '--clean'])
        except subprocess.CalledProcessError as err:
            print(f"An error occurred: {err}")

