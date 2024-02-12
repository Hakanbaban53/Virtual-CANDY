import subprocess


def debian_package_installer(packages):
    for package in packages:
        try:
            subprocess.run(["sudo", "apt-get", "install", package])
        except subprocess.CalledProcessError:
            print(f"There was a problem installing the package: {package}")
