import logging
import sys

from src.svc.secsvc import SecSvc


class LogSvc:
    _loggers: dict[str, "LogSvc"] = {}

    def __new__(cls, name: str):
        if name in cls._loggers:
            return cls._loggers[name]

        instance = super().__new__(cls)

        logger = logging.getLogger(name)
        settings = SecSvc().get_appenv()
        logger.setLevel(settings.loglevel)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(settings.loglevel)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        logger.addHandler(handler)
        logger.propagate = False

        instance._logger = logger
        cls._loggers[name] = instance
        return instance
