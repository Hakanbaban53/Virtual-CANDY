import logging
class LoggingManager:
    """Logging manager for the application."""
    def __init__(self, verbose, dry_run, log_stream=None):
        """Set up the logger."""
        self.logger = logging.getLogger()
        self.logger.handlers = []  # Clear existing handlers
        handler = logging.StreamHandler(log_stream if log_stream else None)
        dry_run_text = " [DRY RUN]" if dry_run else ""
        if verbose:
            formatter = logging.Formatter(f"%(levelname)s {dry_run_text} %(message)s")
        else:
            formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
