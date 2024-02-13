from os import getenv
import subprocess

def check_configure_sudo(username):
    try:
        # Check if the user has sudo privileges
        subprocess.run(['sudo', '-l', '-U', username], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"{username} already has sudo privileges.")
    except subprocess.CalledProcessError:
        print("User not Sudoers")
        # If the user doesn't have sudo privileges, configure sudo
        #configure_sudo(username)

def configure_sudo(username):
    try:
        # Add the user to the sudo group
        subprocess.run(['adduser', username, 'sudo'], check=True)

        print(f"Sudo configured for {username}.")
    except subprocess.CalledProcessError as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    # Replace 'your_username' with the actual username to check and configure
    username_to_check = getenv('USER')

    check_configure_sudo(username_to_check)