from typing import Any, Dict


from postiel_helpers.model.data import DataModel


class LoggingConfig(DataModel):
    logger_name: str
    config: Dict[str, Any]
