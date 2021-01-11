import asyncio

import pytest

from postiel_helpers.action.post.action import PostAction
from postiel_helpers.message_broker.rabbitmq.rabbitmq import RabbitMQ
from test.common import MESSAGE


@pytest.mark.broker
@pytest.mark.asyncio
async def test_rabbitmq(rabbitmq_test_config):
    actions = []

    async def process_data(post_action_bytes: bytes):
        action = PostAction.deserialize(post_action_bytes)

        actions.append(action)

    rabbitmq = await RabbitMQ.initialize(
        config=rabbitmq_test_config, consumers_functions={'_post_consumer': process_data})
    await rabbitmq.send_message(message=MESSAGE)
    await rabbitmq.send_message(message=MESSAGE)
    await asyncio.sleep(1)
    assert actions == [MESSAGE.action, MESSAGE.action]
    await rabbitmq.close()




