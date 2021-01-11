from collections import OrderedDict

from postiel_helpers.action.post.action import PostAction
from postiel_helpers.action.post.author import Author
from postiel_helpers.action.post.file_object import FileObject
from postiel_helpers.action.post.multi_language_field import MultiLanguageField
from postiel_helpers.action.post.post import Post
from postiel_helpers.langauge.language import Language
from postiel_helpers.message_broker.message import Message

MONO_LANGUAGE_FIELD = MultiLanguageField(
    mimetype='text/plain',
    multi_language_value=False,
    field_translations={Language.EN: 'Power', Language.ES: 'Poder'},
    data=12)

MULTI_LANGUAGE_FIELD = MultiLanguageField(
    mimetype='text/plain',
    multi_language_value=True,
    field_translations={Language.EN: 'Name', Language.ES: 'Nombre'},
    data={Language.EN: 'Name', Language.ES: 'Nombre'}
)


POST = Post(
    channel_destination=[1, 2, 3],
    post_id=1,
    author=Author(
        name='a',
        url='test',
        image_url='test.png',
    ),
    template='template1',
    files=OrderedDict((
        ('a', FileObject(url_included=True, public_url='https://test.es', filename='test.png')),
        ('b', FileObject(url_included=False, public_url='https://test.es', filename='test.png')),
        ('c', FileObject(url_included=False, filename='test.png', data=b'test')),
    )),

    data=OrderedDict((
        (
            'power', MONO_LANGUAGE_FIELD
        ), (
            'attribute', MULTI_LANGUAGE_FIELD
        ),
    ))
)

POST_ACTION = PostAction(
    channels=[1, 2, 3],
    posts=[POST]
)


MESSAGE = Message(
    action=POST_ACTION,
    routing_key="test_queue",
    exchange_name="test_exchange",
)

