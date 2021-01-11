"""Author Value Object Module."""
from postiel_helpers.model.data import DataModel


class Author(DataModel):
    """Author Value object. This value object describes author of something."""
    name: str = None
    url: str = None
    image_url: str = None
