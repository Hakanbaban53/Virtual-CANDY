import subprocess

def pip_package_installer(packages):
    for package in packages:
        try:
            subprocess.run(["pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"There was a problem installing the package: {package}")