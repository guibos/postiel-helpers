import os
from abc import ABCMeta
from typing import Optional

import aiofiles
import aiohttp
from aiohttp import ClientSession

from postiel_helpers.abstract.attribute import AbstractAttribute
from postiel_helpers.services.service import Service
from postiel_helpers.action.post.file_value_object import FileValueObject


class HTTP(Service, metaclass=ABCMeta):
    _PUBLIC_URL = AbstractAttribute()

    def __init__(self):
        super().__init__()
        self._session: Optional[ClientSession] = None

    async def _get_file_value_object(self,
                                     url: str,
                                     url_included: bool,
                                     pretty_name=None) -> FileValueObject:
        if not self._download_files:
            return FileValueObject(
                public_url=url,
                pretty_name=pretty_name,
                url_included=url_included,
            )

        path = await self._download_data(url=url)

        if self._PUBLIC_URL:
            return FileValueObject(
                path=path,
                public_url=url,
                pretty_name=pretty_name,
                url_included=url_included,
            )
        return FileValueObject(
            path=path,
            pretty_name=pretty_name,
            url_included=url_included,
        )

    async def _download_data(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                file_data = await resp.read()

        return await self._save_file(file_data=file_data, url=url)

    @staticmethod
    async def _get_filename_from_url(url: str) -> str:
        return os.path.basename(url.split('?')[0])

    async def _save_file(self, file_data: bytes, url: str) -> str:
        path = os.path.join(self._data_directory, await self._get_filename_from_url(url=url))
        async with aiofiles.open(path, mode='wb') as file:
            await file.write(file_data)
        return path