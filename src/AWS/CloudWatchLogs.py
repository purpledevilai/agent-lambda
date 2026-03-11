import logging

def get_logger(name: str = "AWS.CloudWatchLogs", log_level: str = "INFO") -> logging.Logger:
    """
    Returns a logger with a specified name and log level.

    In AWS Lambda the runtime provides its own handler (LambdaLoggerHandler) on the
    root logger that correctly groups multi-line messages into single CloudWatch log
    events.  Adding a custom StreamHandler bypasses that and causes each line to
    appear as a separate event.  So we only set the level here and let Lambda's
    built-in handler take care of formatting and delivery.

    :param name: Logger name.
    :param log_level: Logging level as a string (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    return logger
