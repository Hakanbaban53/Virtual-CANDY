from logging import debug, error
from subprocess import PIPE, CalledProcessError, Popen


def run_command(command, verbose=False, cwd=None):
    """
    Executes a system command with error handling.

    Args:
        command (str): Command to execute.
        verbose (bool): Whether to log the output and errors.
        cwd (str): Working directory to run the command.

    Returns:
        str: Standard output of the command.

    Raises:
        CalledProcessError: If the command fails (non-zero exit code).
    """
    debug(f"Running command: {command}")
    try:
        completed_process = Popen(
            command, shell=True, cwd=cwd, stdout=PIPE, stderr=PIPE, text=True
        )
        stdout, stderr = completed_process.communicate()
        
        if completed_process.returncode != 0:
            if verbose:
                error(f"Error output: {stderr.strip()}")
                        
        if verbose:
            if stdout.strip():
                debug(f"Progress/Info: {stdout.strip()}")
            if stderr.strip():  # Log diagnostic/progress info if needed
                debug(f"Progress/Info: {stderr.strip()}")
        
        return stdout
    except CalledProcessError as e:
        error(f"An error occurred: {e.stderr.strip()}")
        raise
