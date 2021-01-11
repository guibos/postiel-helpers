"""Custom Field Value Object Module."""
from typing import Dict, Any, List

from postiel_helpers.action.post.translated_field import TranslatedField
from postiel_helpers.langauge.language import Language
from postiel_helpers.model.data import DataModel


class MultiLanguageField(DataModel):
    """Custom Field Value Object. This describes a custom field and his value. Each receiver can add custom fields that
    will be attached in a Publication."""
    field_translations: Dict[Language, str]
    multi_language_value: bool
    mimetype: str
    data: Any

    def get_translated_field(self, language_preference: List[Language]) -> TranslatedField:
        field_name = None
        language = None
        for language in language_preference:
            if language in self.field_translations:
                field_name = self.field_translations[language]
                break

        if not field_name:
            language, field_name = next(iter(self.field_translations.items()))

        if not self.multi_language_value:
            data = self.data
        else:
            data = self.data[language]

        return TranslatedField(field_name=field_name, data=data, mimetype=self.mimetype)
