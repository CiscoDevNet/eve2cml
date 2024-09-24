import logging

import pytest

from eve2cml.log import initialize_logging


@pytest.mark.parametrize(
    "nocolor",
    [True, False],
)
def test_initialize_logging(caplog, nocolor):
    initialize_logging("DEBUG", nocolor=nocolor)

    # Verify log messages are colorized
    logger = logging.getLogger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Retrieve captured log records
    log_records = caplog.records

    # Verify colored log levels
    if not nocolor:
        for record in log_records:
            assert record.levelname.startswith("\033[")
            assert record.levelname.endswith("\033[0m")

    # Verify log messages content
    assert log_records[0].message == "Debug message"
    assert log_records[1].message == "Info message"
    assert log_records[2].message == "Warning message"
    assert log_records[3].message == "Error message"
    assert log_records[4].message == "Critical message"
