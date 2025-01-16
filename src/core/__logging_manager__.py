import logging

class LoggingManager:
    """Logging manager for the application."""
    def __init__(self, verbose, dry_run):
        """Set up the logger."""
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        dry_run_text = " [DRY RUN]" if dry_run else ""
        if verbose:
            formatter = logging.Formatter(f"%(levelname)s {'-'+dry_run_text+'-' if dry_run else ''} %(message)s")
        else:
            formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)