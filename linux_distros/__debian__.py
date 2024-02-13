from os import getenv
import subprocess

import requests

def debian_package_installer(packages):
    subprocess.call(['su'] )
    for data in packages:
        value = data.get("value", "")
        try:
            if type == "install-package":
                subprocess.call(['apt', 'list', 'installed', value])
            elif type == "install-package-flatpak":
                subprocess.call(['flatpak', 'list', '|', 'grep', value])
            else:
                type_of_action(data)
        except subprocess.CalledProcessError:
            type_of_action(data)

def type_of_action(data):
    current_user = getenv('USER')
    target_directory = f'/home/{current_user}/'
    type = data.get("type", "")
    value = data.get("value", "")
    name = data.get("name", "")
    try:
        if type == "install-package":
            packages_to_install = value.split()  # Split the package names into a list
            subprocess.call(['apt', 'install'] + packages_to_install)

        elif type == "get-keys":
            key_url = 'https://download.docker.com/linux/ubuntu/gpg'
            response = requests.get(key_url)
    
            if response.status_code == 200:
             # Save the GPG key to /etc/apt/keyrings/docker.asc
               with subprocess.Popen(['sudo', 'tee', '/etc/apt/keyrings/docker.asc'], stdin=subprocess.PIPE) as key_process:
                key_process.communicate(response.content)
            
                subprocess.run(['chmod', 'a+r', '/etc/apt/keyrings/docker.asc'])
                print("Docker repository keys installed successfully.")
            else:
                print(f"Failed to fetch Docker repository GPG key. Status code: {response.status_code}")

            subprocess.run(['chmod', 'a+r', '/etc/apt/keyrings/docker.asc'])

            subprocess.run([
                'bash', '-c',
                'echo', '"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable"', '|', 'tee', '/etc/apt/sources.list.d/docker.list > /dev/null'
            ])
            subprocess.call(['apt', 'update'] )

            print("Docker repository keys installed successfully.")

        elif type == "local-package":
            subprocess.run(
                [
                    "wget",
                    "--show-progress",
                    "--progress=bar:force",
                    "-O",
                    f"{name}.package.deb",
                    value,
                ], cwd=target_directory
            )
            subprocess.run(["apt-get", "--fix-broken", "install", f"{name}.package.deb"], cwd=target_directory)

        elif type == "remove-package":
            packages_to_remove = value.split()  # Split the package names into a list
            subprocess.call(['apt', 'remove'] + packages_to_remove)


        elif type == "install-service":
            subprocess.call(['systemctl', 'restart', value])
            subprocess.call(['systemctl', 'enable', value])

        elif type == "add-group":
            subprocess.call(['usermod', '-aG', value, current_user])

        elif type == "install-package-flatpak":
            subprocess.call(['flatpak', 'install', '-y', value])
            
    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")

