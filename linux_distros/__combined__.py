from subprocess import run, PIPE, CalledProcessError, check_output
from os import path, devnull, getenv
from time import sleep
from functions.__special_install_selector__ import SelectSpecialInstaller

def package_manager(distro, packages, output, action, dry_run):
    hide = open(devnull, "w") if not output else None

    if distro in {"debian", "ubuntu"} and not dry_run:
        run(["sudo", "apt", "update"], stderr=hide, stdout=hide)

    for package in packages:
        name = package.get("name", "")
        check_value = package.get("check_value", "")
        package_type = package.get("type", "")
        check_script = package.get("check_script", [])

        try:
            if package_type in {"package", "url-package", "local-package", "AUR-package"}:
                handle_standard_package(distro, package, check_value, action, dry_run, hide)
            elif package_type == "special-package":
                SelectSpecialInstaller(hide, action, package, distro, dry_run)
            elif package_type == "remove-package":
                handle_removable_package(distro, package, check_value, action, dry_run, hide)
            elif package_type == "get-keys":
                handle_repo_keys(distro, package, check_script, action, dry_run, hide)
            elif package_type in {"service", "group"}:
                handle_service_or_group(distro, package, action, dry_run, hide)
            elif package_type == "package-flatpak":
                handle_flatpak_package(package, check_value, action, dry_run, hide)
        except CalledProcessError as e:
            handle_error(e, check_value, action, name, dry_run, package, hide)

def handle_standard_package(distro, package, check_value, action, dry_run, hide):
    if distro == "arch":
        result = run(["pacman", "-Q"] + check_value.split(), stdout=PIPE, stderr=PIPE)
    elif distro in {"debian", "ubuntu"}:
        result = run(["apt", "list", "--installed"] + check_value.split(), stdout=PIPE, stderr=PIPE)
    elif distro == "fedora":
        result = run(["dnf", "list", "--installed", check_value], stdout=PIPE, stderr=PIPE)

    output = result.stdout.decode("utf-8").lower()
    if check_value.lower() not in output:
        if action == "install":
            print(f"{package['name']} not installed. Installing...")
            if not dry_run:
                package_installer(distro, package, hide)
        elif action == "remove":
            print(f"{package['name']} not installed. Skipping...")
    else:
        if action == "install":
            print(f"{package['name']} already installed. Skipping...")
        elif action == "remove":
            print(f"{package['name']} removing...")
            if not dry_run:
                package_remover(distro, package, hide)

def handle_removable_package(distro, package, check_value, action, dry_run, hide):
    if distro == "arch":
        result = run(["pacman", "-Q"] + check_value.split(), stdout=PIPE, stderr=PIPE)
    elif distro in {"debian", "ubuntu"}:
        result = run(["apt", "list", "--installed"] + check_value.split(), stdout=PIPE, stderr=PIPE)
    elif distro == "fedora":
        result = run(["dnf", "list", "installed"] + check_value.split(), stdout=PIPE, stderr=PIPE)

    if "error" not in result.stderr.decode("utf-8").lower():
        if action == "install":
            print(f"{package['name']} removing...")
            if not dry_run:
                package_remover(distro, package, hide)
        elif action == "remove":
            print(f"{package['name']} not installed. Skipping...")

def handle_repo_keys(distro, package, check_script, action, dry_run, hide):
    for path_key in check_script:
        if not path_key:
            print("Skipping...")
            continue

        if path.exists(path_key):
            if action == "install":
                print(f"{package['name']} repo key installed. Skipping...")
            elif action == "remove":
                print(f"{package['name']} repo key removing...")
                if not dry_run:
                    package_remover(distro, package, hide)
        else:
            if action == "install":
                print(f"{package['name']} repo key not installed. Installing...")
                if not dry_run:
                    package_installer(distro, package, hide)
            elif action == "remove":
                print(f"{package['name']} repo key not installed. Skipping...")

def handle_service_or_group(distro, package, action, dry_run, hide):
    if action == "install":
        print(f"{package['name']} service/group (re)installing...")
        if not dry_run:
            package_installer(distro, package, hide)
    elif action == "remove":
        print("Skipping the service/group...")

def handle_flatpak_package(package, check_value, action, dry_run, hide):
    result = run(["flatpak", "list"], stdout=PIPE, stderr=PIPE)

    if check_value not in result.stdout.decode("utf-8"):
        if action == "install":
            print(f"{package['name']} not installed. Installing...")
            if not dry_run:
                package_installer("fedora", package, hide)
        elif action == "remove":
            print(f"{package['name']} not installed. Skipping...")
    else:
        if action == "install":
            print(f"{package['name']} was installed. Skipping...")
        elif action == "remove":
            print(f"{package['name']} removing...")
            if not dry_run:
                package_remover("fedora", package, hide)

def handle_error(e, check_value, action, name, dry_run, package, hide):
    error_message = e.stderr.decode("utf-8").lower()
    if check_value not in error_message:
        if action == "install":
            print(f"{name} not installed. Installing...")
            if not dry_run:
                package_installer("fedora", package, hide)
        elif action == "remove":
            print(f"{name} not installed. Skipping...")
    else:
        print(f"An error occurred: {e}")

def package_installer(distro, package, hide):
    current_user = getenv("USER")
    target_directory = f"/home/{current_user}/"
    package_type = package.get("type", "")
    install_value = package.get("install_value", "")

    try:
        if distro == "arch":
            if package_type == "package":
                run(["sudo", "pacman", "-S", install_value, "--noconfirm"], stderr=hide, stdout=hide)
            elif package_type == "local-package":
                local_package_installer(install_value, target_directory, hide)
            elif package_type == "service":
                run(["sudo", "systemctl", "restart", install_value], stderr=hide, stdout=hide)
                run(["sudo", "systemctl", "enable", install_value], stderr=hide, stdout=hide)
            elif package_type == "group":
                run(["sudo", "usermod", "-aG", install_value, current_user], stderr=hide, stdout=hide)
            elif package_type == "repo-flathub":
                run(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", install_value], stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "install", "-y", install_value], stderr=hide, stdout=hide)
            elif package_type == "AUR-package":
                handle_aur_package(install_value, target_directory, hide)

        elif distro in {"debian", "ubuntu"}:
            if package_type == "package":
                run(["sudo", "apt", "install", "-y"] + install_value.split(), stderr=hide, stdout=hide)
            elif package_type == "get-keys":
                for command in package.get("install_script", []):
                    run(command, shell=True, stderr=hide, stdout=hide)
            elif package_type == "local-package":
                handle_local_package(install_value, target_directory, hide)
            elif package_type == "service":
                run(["sudo", "systemctl", "restart", install_value], stderr=hide, stdout=hide)
                run(["sudo", "systemctl", "enable", install_value], stderr=hide, stdout=hide)
            elif package_type == "group":
                run(["sudo", "usermod", "-aG", install_value, current_user], stderr=hide, stdout=hide)
            elif package_type == "repo-flathub":
                run(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", install_value], stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "install", "-y", install_value], stderr=hide, stdout=hide)

        elif distro == "fedora":
            if package_type == "package":
                run(["sudo", "dnf", "install", "-y"] + install_value.split(), stderr=hide, stdout=hide)
            elif package_type == "get-keys":
                for command in package.get("install_script", []):
                    run(command, shell=True, stderr=hide, stdout=hide)
            elif package_type == "url-package":
                install_value = replace_fedora_version(install_value)
                run(["sudo", "dnf", "install", "-y", install_value], stderr=hide, stdout=hide)
            elif package_type == "local-package":
                handle_local_package(install_value, target_directory, hide)
            elif package_type == "service":
                run(["sudo", "systemctl", "restart", install_value], stderr=hide, stdout=hide)
                run(["sudo", "systemctl", "enable", install_value], stderr=hide, stdout=hide)
            elif package_type == "group":
                run(["sudo", "usermod", "-aG", install_value, current_user], stderr=hide, stdout=hide)
            elif package_type == "repo-flathub":
                run(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", install_value], stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "install", "-y", install_value], stderr=hide, stdout=hide)

    except CalledProcessError as err:
        print(f"An error occurred: {err}")

def package_remover(distro, package, hide):
    package_type = package.get("type", "")
    remove_value = package.get("remove_value", "")

    try:
        if distro == "arch":
            if package_type in {"package", "AUR-package", "local-package"}:
                run(["sudo", "pacman", "-R", remove_value, "--noconfirm"], stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "remove", "-y", remove_value], stderr=hide, stdout=hide)

        elif distro in {"debian", "ubuntu"}:
            if package_type in {"package", "url-package", "local-package", "remove-package"}:
                run(["sudo", "apt", "remove", "-y"] + remove_value.split(), stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "remove", "-y", remove_value], stderr=hide, stdout=hide)
            elif package_type == "get-keys":
                for command in package.get("remove_script", []):
                    run(command, shell=True, stderr=hide, stdout=hide)

        elif distro == "fedora":
            if package_type in {"package", "url-package", "local-package", "remove-package"}:
                run(["sudo", "dnf", "remove", "-y"] + remove_value.split(), stderr=hide, stdout=hide)
            elif package_type == "package-flatpak":
                run(["sudo", "flatpak", "remove", "-y", remove_value], stderr=hide, stdout=hide)
            elif package_type == "get-keys":
                for command in package.get("remove_script", []):
                    run(command, shell=True, stderr=hide, stdout=hide)

    except CalledProcessError as err:
        print(f"An error occurred: {err}")

def local_package_installer(install_value, target_directory, hide):
    run(["wget", "--progress=bar:force", "-O", "local.package.pkg.tar.zst", install_value], cwd=target_directory, stderr=hide, stdout=hide)
    run(["sudo", "pacman", "-U", "local.package.pkg.tar.zst", "--noconfirm"], cwd=target_directory, stderr=hide, stdout=hide)
    run(["sudo", "rm", "-f", "local.package.pkg.tar.zst"], cwd=target_directory, stderr=hide, stdout=hide)

def handle_aur_package(install_value, target_directory, hide):
    repository_directory = f"{target_directory}/{install_value}"
    run(["git", "clone", f"https://aur.archlinux.org/{install_value}.git"], cwd=target_directory)
    sleep(10)
    run(["makepkg", "-si", "--noconfirm"], cwd=repository_directory, stderr=hide, stdout=hide)
    sleep(10)
    run(["sudo", "rm", "-rf", install_value], cwd=target_directory, stderr=hide, stdout=hide)

def replace_fedora_version(value):
    fedora_version = check_output(["rpm", "-E", "%fedora"], text=True).strip()
    return value.replace("$(rpm -E %fedora)", fedora_version)

def handle_local_package(install_value, target_directory, hide):
    local_path = path.join(target_directory, "local.package.deb")
    run(["wget", "--progress=bar:force", "-O", local_path, install_value])
    run(["sudo", "dpkg", "-i", local_path], stderr=hide, stdout=hide)
    run(["sudo", "apt", "--fix-broken", "install", "-y"], stderr=hide, stdout=hide)
    run(["sudo", "rm", "-f", local_path], stderr=hide, stdout=hide)