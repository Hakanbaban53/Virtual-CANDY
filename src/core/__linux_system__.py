from logging import error, info
from subprocess import CalledProcessError
from core.__command_handler__ import run_command
from core.__constants__ import CURRENT_USER

def usermod_group(group, action, dry_run, verbose):
    try:
        if action == "install":
            info(f"Adding {CURRENT_USER} to {group}...")
            if not dry_run:
                run_command(f"sudo usermod -aG {group} {CURRENT_USER}", verbose)
        elif action == "remove":
            info(f"Removing {CURRENT_USER} from {group}...")
            if not dry_run:
                run_command(f"sudo deluser {CURRENT_USER} {group}", verbose)
    except CalledProcessError as err:
        error(f"An error occurred: {err}")


def systemd_service(service, action, dry_run, verbose):
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

