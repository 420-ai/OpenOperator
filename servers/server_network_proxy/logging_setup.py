import logging.config
import os


def configure_logging(directory: str) -> None:

    os.makedirs(directory, exist_ok=True)
    LOG_FILE = os.path.join(directory, "server_network_proxy.log")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "detailed",
                "level": "FATAL",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": "FATAL",
            },
            "default": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "detailed",
                "level": "FATAL",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "FATAL",
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.basicConfig(level=logging.FATAL)
