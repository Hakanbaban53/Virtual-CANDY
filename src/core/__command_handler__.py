from logging import error, info
from subprocess import PIPE, CalledProcessError, Popen

def run_command(command, verbose=None, cwd=None):
    """
    Executes a system command with error handling.

    Args:
        command (str): Command to execute.
        verbose (file-like): Output stream for verbose logs.

    Returns:
        str: Command output.
    """
    try:
        completed_process = Popen([command], shell=True, cwd=cwd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = completed_process.communicate()
        if stderr and verbose:
            error(f"An error occurred: {stderr.decode('utf-8')}")
        elif stdout and verbose:
            info(f"Output: {stdout.decode('utf-8')}")
    except CalledProcessError as e:
        error(f"An error occurred: {e}")