"""File Value Object Module."""
from typing import Optional


from postiel_helpers.model.data import DataModel


class FileObject(DataModel):
    """This value object is abstraction how app need to interact with a file. It's possible that is only available on
    file system or a public url."""
    url_included: bool
    filename: Optional[str] = None
    public_url: Optional[str] = None
    data: Optional[bytes] = None
