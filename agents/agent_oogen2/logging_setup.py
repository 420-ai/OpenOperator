import logging.config
import os

def configure_logging(directory: str) -> None:

    LOG_FILE = os.path.join(directory, "app.log")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
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
                "level": "DEBUG",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": "DEBUG",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "loggers": {
            "urllib3": {  
                "level": "INFO",
                "propagate": False,
            },
            "PIL": {  
                "level": "INFO",
                "propagate": False,
            },
            "openai": {  
                "level": "INFO",
                "propagate": False,
            },
            "httpcore": {
                "level": "INFO",
                "propagate": False,
            },
            "autogen_core": {
                "level": "ERROR",
                "propagate": False,
            },
            "httpx": {
                "level": "ERROR",
                "propagate": False,
            },
            "autogen_agentchat": {
                "level": "ERROR",
                "propagate": False,
            },
            "asyncio": {
                "level": "ERROR",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)