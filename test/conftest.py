import pytest

pytest_plugins = ['pytest_docker_fixtures']


@pytest.fixture
def rabbitmq_test_config(rabbitmq):
    return {
        "common": {
            "logger_name": "ChallongeRabbitMQ",
        },
        'connection': {
            'host': rabbitmq[0],
            'port': int(rabbitmq[1])
        },
        "create": {
            "queues": [
                {"name": "test_queue", "durable": True}
            ],
            "exchanges": [
                {"name": "test_exchange", "durable": True}
            ],
            "bindings": {
                "test_queue": ["test_exchange"]
            }
        },
        "consumer": [
            {"queue_name": "test_queue", "consumer_name": "_post_consumer"}
        ]
    }