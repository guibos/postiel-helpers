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
            # 'host': '127.0.0.1',
            # 'port': '5672'
        },
        "create": {
            "queues": [
                {"name": "test_queue", "durable": True},
                {"name": "test_dead_queue", "durable": True}
            ],
            "exchanges": [
                {"name": "test_exchange", "durable": True},
                {"name": "test_dead_exchange", "durable": True}
            ],
            "bindings": [
                {"queue_name": "test_queue", "exchange_name": "test_exchange", "routing_key": "test_queue"}
            ]
        },
        "consumers": [
            {
                "queue_name": "test_queue",
                "consumer_name": "_post_consumer",
                "failed_message_routing": {"routing_key": "test_dead_queue", "exchange_name": "test_dead_exchange"}
            }
        ],
        "failed_message_consumer": [
            {
                "queue_name": "test_queue",
                "consumer_name": "_post_consumer",
            }
        ]
    }