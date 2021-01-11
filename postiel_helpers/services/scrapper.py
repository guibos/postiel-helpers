import urllib.parse
from abc import ABCMeta
from typing import Optional, Tuple

import aiohttp
from bs4 import element

from postiel_helpers.abstract.attribute import AbstractAttribute
from postiel_helpers.services.http import HTTP


class Scrapper(HTTP, metaclass=ABCMeta):
    _BANNED_ALT: Tuple[str] = tuple()
    _DOMAIN: str = AbstractAttribute()
    _MAX_IMAGES: Optional[int] = None
    _URLS_INCLUDED: bool = AbstractAttribute()

    async def _prepare(self):
        self._session = aiohttp.ClientSession()

    async def _get_images(self, data: element, title: str) -> element:
        images = []
        img_urls = []
        img_tags = data.find_all('img')

        for img_tag in img_tags:
            if 'alt' in img_tag.attrs:
                if img_tag.attrs['alt'] in self._BANNED_ALT:
                    continue
            img_url = img_tag.attrs['src']
            if img_url in img_urls:
                continue
            img_urls.append(img_url)
            if not urllib.parse.urlparse(img_url).netloc:
                img_url = urllib.parse.urljoin(self._DOMAIN, img_url)
            image = await self._get_file_value_object(url=img_url,
                                                      pretty_name=title,
                                                      url_included=self._URLS_INCLUDED)

            images.append(image)
            if len(img_urls) == self._MAX_IMAGES:
                return images
        return images
