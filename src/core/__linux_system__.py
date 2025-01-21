from logging import error
from os import getenv
from subprocess import CalledProcessError
from core.__command_handler__ import run_command

def usermod_group_installer(group, action, verbose):
    try:
        if action == "install":
            run_command(f"sudo usermod -aG {group} {getenv('USER')}", verbose)
        elif action == "remove":
            run_command(f"sudo deluser {getenv('USER')} {group}", verbose)
    except CalledProcessError as err:
        error(f"An error occurred: {err}")


def systemd_service_installer(service, action, verbose):
    try:
        if action == "install":
            run_command(f"sudo systemctl restart {service}", verbose)
            run_command(f"sudo systemctl enable {service}", verbose)
        elif action == "remove":
            run_command(f"sudo systemctl stop {service}", verbose)
            run_command(f"sudo systemctl disable {service}", verbose)
    except CalledProcessError as err:
        error(f"An error occurred: {err}")

