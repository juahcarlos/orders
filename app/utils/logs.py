import os
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
AIOLIB_LOG_LEVEL = os.getenv("AIOLIB_LOG_LEVEL", "INFO").upper()

LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

log_level = LEVELS.get(LOG_LEVEL, logging.DEBUG)
aiokafka_level = LEVELS.get(AIOLIB_LOG_LEVEL, logging.INFO)

logging.basicConfig(level=log_level)
log = logging.getLogger(__name__)

# force aiokafka logger
ak_logger = logging.getLogger("aiokafka")
ak_logger.setLevel(aiokafka_level)
ak_logger.propagate = False
