import asyncio
from typing import Any, Dict, Callable, List

from postiel_helpers.action.post.action import PostAction
from postiel_helpers.message_broker.service_consumer import ServiceConsumer
from postiel_helpers.message_broker.interface import MessageBrokerInterface
from postiel_helpers.model.field import field
from postiel_helpers.services.service import Service
from test.common import MESSAGE, POST_ACTION


class BrokerMock(MessageBrokerInterface):
    def initialize(cls, config: Dict[str, Any], service_consumers: Dict[str, Callable] = field(default_factory=dict)):
        pass


def test_service_rabbitmq(
        rabbitmq_test_config
):
    config = {
        "logging": {
            "logger_name": "Challonge",
            "config": {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                    },
                },
                "handlers": {
                    "stream": {
                        "level": "INFO",
                        "formatter": "standard",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",  # Default is stderr
                    },
                },
                "loggers": {
                    "Challonge": {
                        "handlers": [
                            "stream",
                        ],
                        "level": "DEBUG"
                    },
                    "ChallongeRabbitMQ": {
                        "handlers": [
                            "stream",
                        ],
                        "level": "DEBUG"
                    }
                }
            }
        },
        "message_brokers": {
            "RabbitMQ": {
                "class_name": "RabbitMQ",
                "config": rabbitmq_test_config
            }
        }
    }

    class MockService(Service):
        _CONFIG_DIRECTORY = ""
        _CONFIG_FILENAME = ""

        def __init__(self):
            super().__init__()
            self.actions: List[PostAction] = []
            self._consumer_functions = {'_post_consumer': ServiceConsumer(
                func=self._post_consumer, action_type=PostAction)}

        async def _start(self) -> None:
            await self._brokers["RabbitMQ"].send_message(MESSAGE)
            await asyncio.sleep(1)

        async def _get_config_data(self) -> Dict[str, Any]:
            return config

        async def _post_consumer(self, action: PostAction):
            self.actions.append(action)

    service = MockService()
    service.run()
    assert service.actions == [POST_ACTION]
