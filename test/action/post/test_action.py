
from postiel_helpers.action.post.action import PostAction
from test.common import POST_ACTION


def test_post_action_serialize():
    assert POST_ACTION == PostAction.deserialize(POST_ACTION.serialize())
