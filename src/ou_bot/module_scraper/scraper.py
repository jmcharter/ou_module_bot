from dataclasses import dataclass

import requests
from requests import Response

from ou_bot.module_scraper.config import ScraperConfig


@dataclass
class Scraper:
    config: ScraperConfig

    def _get_request(self) -> Response:
        url = self.config.url
        return requests.get(url)

    def scrape_text(self) -> str:
        r = self._get_request()
        return r.text
