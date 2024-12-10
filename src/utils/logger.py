import logging
import os
from logging.handlers import TimedRotatingFileHandler


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonType):
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "app.log")

        self.logger = logging.getLogger("my_app")
        self.logger.setLevel(self.log_level)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # Rotating File Handler
        file_handler = TimedRotatingFileHandler(
            self.log_file, when="midnight", interval=1, backupCount=7
        )
        file_handler.setLevel(self.log_level)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Adding Handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # Handling dynamic log levels
        numeric_level = getattr(logging, self.log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")
        self.logger.setLevel(numeric_level)

    def get_logger(self):
        return self.logger


# Usage
# from logger import Logger
# log = Logger().get_logger()
# log.info("This is an info message")
