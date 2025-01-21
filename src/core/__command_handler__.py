from logging import error, info
from subprocess import CalledProcessError, run

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
        completed_process = run([command], capture_output=True, shell=True, cwd=cwd)
        if completed_process.stderr and verbose:
            error(f"An error occurred: {completed_process.stderr.decode(errors='replace')}")
        elif completed_process.stdout and verbose:
            info(f"Output: {completed_process.stdout.decode(errors='replace')}")
    except CalledProcessError as e:
        error(f"An error occurred: {e}")