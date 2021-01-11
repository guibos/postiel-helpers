import logging
import logging.config

import aiolog

from postiel_helpers.config.logging import LoggingConfig


class LoggerMixin:
    def __init__(self):
        self._logger = logging.getLogger()

    async def _load_logger_config(self, config: LoggingConfig) -> None:
        if config:
            logging.config.dictConfig(config.config)
        aiolog.start()
        self._logger = logging.getLogger(config.logger_name)

    @staticmethod
    async def _stop() -> None:
        await aiolog.stop()
