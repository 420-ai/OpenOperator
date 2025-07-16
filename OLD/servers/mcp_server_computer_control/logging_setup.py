import logging.config
import os

def configure_logging(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    LOG_FILE = os.path.join(directory, "mcp_computer_control_server.log")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "%"
            },
            "uvicorn_format": {
                "format": "%(message)s"
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": "DEBUG",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "detailed",
                "level": "DEBUG",
            },
            "uvicorn_console": {
                "class": "logging.StreamHandler",
                "formatter": "uvicorn_format",
                "level": "INFO",
            },
            "uvicorn_file": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "uvicorn_format",
                "level": "INFO",
            },
        },

        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },

        "loggers": {
            "uvicorn": {
                "handlers": ["uvicorn_console", "uvicorn_file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["uvicorn_console", "uvicorn_file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["uvicorn_console", "uvicorn_file"],
                "level": "INFO",
                "propagate": False
            },
            "kubernetes.client.rest": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False
            },
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)
