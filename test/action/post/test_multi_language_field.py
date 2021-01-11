from postiel_helpers.action.post.translated_field import TranslatedField
from postiel_helpers.langauge.language import Language
from test.common import MONO_LANGUAGE_FIELD, MULTI_LANGUAGE_FIELD


def test_mono_language_preference():
    translated_field = MONO_LANGUAGE_FIELD.get_translated_field([Language.AB, Language.EN])
    assert translated_field == TranslatedField(field_name='Power', mimetype='text/plain', data=12)


def test_mono_language_no_preference():
    translated_field = MONO_LANGUAGE_FIELD.get_translated_field([Language.CA])
    assert translated_field == TranslatedField(field_name='Power', mimetype='text/plain', data=12)


def test_multi_language_preference():
    translated_field = MULTI_LANGUAGE_FIELD.get_translated_field([Language.AB, Language.EN])
    assert translated_field == TranslatedField(field_name='Name', mimetype='text/plain', data='Name')


def test_multi_language_no_preference():
    translated_field = MULTI_LANGUAGE_FIELD.get_translated_field([Language.CA])
    assert translated_field == TranslatedField(field_name='Name', mimetype='text/plain', data='Name')
