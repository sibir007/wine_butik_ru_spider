from pathlib import Path

import scrapy
from scrapy.http import Response


class WinesSpider(scrapy.Spider):
    name = "wines"

    async def start(self):
        urls = [
            "https://wine-butik.ru/wine/?limit=40&page=1",
            "https://wine-butik.ru/wine/?limit=40&page=2",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> None:
        page = response.url[-1]
        filename = f"wines-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")