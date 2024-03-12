import logging

# Define color codes for different log levels
COLOR_CODES = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bold Red
    "RESET": "\033[0m",  # Reset
}


# Custom formatter for colorized output
class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        log_level = record.levelname
        if log_level in COLOR_CODES:
            color_code = COLOR_CODES[log_level]
            # record.msg = f"{color_code}{record.msg}{COLOR_CODES['RESET']}"
            record.levelname = f"{color_code}{record.levelname}:{COLOR_CODES['RESET']}"

        return super().format(record)


def initialize_logging(level_str: str, nocolor: bool):
    # get the root logger
    logger = logging.getLogger()

    # Set level
    level = logging._nameToLevel.get(level_str.upper(), logging.INFO)
    logger.setLevel(level)

    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter and set to handler
    log_format = "%(levelname)s [%(module)s:%(lineno)d] %(message)s"
    if nocolor:
        formatter = logging.Formatter(log_format)
    else:
        formatter = ColorFormatter(log_format)
    ch.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(ch)

    # # Test logging
    # logger.debug('Debug message')
    # logger.info('Info message')
    # logger.warning('Warning message')
    # logger.error('Error message')
    # logger.critical('Critical message')
