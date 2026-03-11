import logging

def get_logger(name: str = "AWS.CloudWatchLogs", log_level: str = "INFO") -> logging.Logger:
    """
    Returns a logger with a specified name and log level.

    In AWS Lambda the runtime provides its own handler (LambdaLoggerHandler) on the
    root logger that correctly groups multi-line messages into single CloudWatch log
    events.  Adding a custom StreamHandler bypasses that and causes each line to
    appear as a separate event.  So we only set the level here and let Lambda's
    built-in handler take care of formatting and delivery.

    We also set the root logger level so that child loggers (e.g. those created
    via logging.getLogger(__name__) in other modules) inherit the correct level
    without each needing to call get_logger explicitly.

    :param name: Logger name.
    :param log_level: Logging level as a string (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
