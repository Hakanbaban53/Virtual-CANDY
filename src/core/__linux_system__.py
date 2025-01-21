from logging import error, info
from os import getenv
from subprocess import CalledProcessError
from core.__command_handler__ import run_command

def usermod_group_installer(group, action, dry_run, verbose):
    try:
        if action == "install":
            info(f"Adding {getenv('USER')} to {group}...")
            if not dry_run:
                run_command(f"sudo usermod -aG {group} {getenv('USER')}", verbose)
        elif action == "remove":
            info(f"Removing {getenv('USER')} from {group}...")
            if not dry_run:
                run_command(f"sudo deluser {getenv('USER')} {group}", verbose)
    except CalledProcessError as err:
        error(f"An error occurred: {err}")


def systemd_service_installer(service, action, dry_run, verbose):
    try:
        if action == "install":
            info(f"Installing {service}...")
            if not dry_run:
                run_command(f"sudo systemctl restart {service}", verbose)
                run_command(f"sudo systemctl enable {service}", verbose)
        elif action == "remove":
            info(f"Removing {service}...")
            if not dry_run:
                run_command(f"sudo systemctl stop {service}", verbose)
                run_command(f"sudo systemctl disable {service}", verbose)
    except CalledProcessError as err:
        error(f"An error occurred: {err}")

