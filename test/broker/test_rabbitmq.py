import asyncio

import pytest

from postiel_helpers.action.post.action import PostAction
from postiel_helpers.message_broker.service_consumer import ServiceConsumer
from postiel_helpers.message_broker.rabbitmq.rabbitmq import RabbitMQ
from test.common import MESSAGE


@pytest.mark.broker
@pytest.mark.asyncio
async def test_rabbitmq(rabbitmq_test_config):
    actions = []

    async def process_data(post_action: PostAction) -> None:
        actions.append(post_action)

    rabbitmq = await RabbitMQ.initialize(
        config=rabbitmq_test_config, service_consumers={'_post_consumer': ServiceConsumer(
            func=process_data, action_type=PostAction)}, close_grace=1)
    await asyncio.gather(
        rabbitmq.send_message(message=MESSAGE),
        rabbitmq.send_message(message=MESSAGE)
    )
    await asyncio.sleep(1)
    await rabbitmq.close()
    assert actions == [MESSAGE.action, MESSAGE.action]

    assert rabbitmq._consumers[0].task.done()




