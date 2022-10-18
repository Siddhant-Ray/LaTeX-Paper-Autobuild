import os
import sys
from logging import *
from logging.handlers import RotatingFileHandler

from locations import script_log_file


def create_logger():
    logger = getLogger("logger")

    logger.setLevel(DEBUG)

    console_formatter = Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    message_formatter = Formatter("[%(levelname)s] %(message)s")

    # add a rotating handler
    need_roll_over = os.path.isfile(script_log_file)
    file_handler = RotatingFileHandler(script_log_file, backupCount=5, encoding="utf8")
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)

    # force rollover if files exists
    if need_roll_over:
        file_handler.doRollover()

    # add console handler
    console_handler = StreamHandler(sys.stdout)
    console_handler.setLevel(INFO)
    console_handler.setFormatter(message_formatter)
    logger.addHandler(console_handler)

    return logger


logger = create_logger()


def report_error(error, details=None, solutions=None):
    """
    :param error: string
    :param details: list of strings
    :param solutions: list of strings
    """
    # details
    if details is not None:
        details = ["  > " + s for s in details]
        details = ["  DETAILS:"] + details
        details = "\n".join(details)
    # solutions
    if solutions is not None:
        solutions = ["  > " + s for s in solutions]
        solutions = ["  SOLUTIONS:"] + solutions
        solutions = "\n".join(solutions)
    msg = error
    if details is not None:
        msg += "\n" + details
    if solutions is not None:
        msg += "\n" + solutions
    logger.error(msg)
