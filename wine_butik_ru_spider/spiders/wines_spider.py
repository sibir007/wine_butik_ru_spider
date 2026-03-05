# from collections.abc import Iterator
from collections.abc import Generator
from pathlib import Path
from typing import Iterable, AsyncGenerator

from parsel import SelectorList
import scrapy
from scrapy.http import Response, Request


class WinesSpider(scrapy.Spider):
    name = "wines"
    query = "/wine/?limit=40&{}"

    async def start(self) -> AsyncGenerator[Request, None]:
        base_url = self.settings.get("BASE_URL")
        urls = [
            f"{base_url}{self.query.format('page=1')}",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_cards_page)

    def parse_cards_page(self, response: Response) -> Generator[dict[str, str], None, None]:
    # def parse_cards_page(self, response: Response) -> Generator[Request, None, None]:
        wine_cards = response.css("div.catalog-item")
        wine_cards_url = (card.css("div.catalog-item__desc h2 a::attr(href)").get() for card in wine_cards)
        yield from ({'url': url} for url in wine_cards_url if url)
        # yield from (Request(url=url, callback=self.parse_wine_page) for url in wine_cards_url if url)
        
        # page = response.url[-1]
        # filename = f"wines-{page}.html"
        # Path(filename).write_text(response.body.decode("cp1251"))
        # self.log(f"Saved file {filename}")

    def parse_wine_page(self, response: Response):
        pass