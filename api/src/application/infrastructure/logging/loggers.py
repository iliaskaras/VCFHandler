import logging
import sys
from logging import Logger


def configure_application_logger(name: str) -> Logger:
    """
    Configuration of the application stderr channel logs.

    :param name: Logger name.

    :return: The application Logger.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s")
    )

    logger.addHandler(stream_handler)

    return logger


LOGGER = configure_application_logger("VCF LOGGER")
