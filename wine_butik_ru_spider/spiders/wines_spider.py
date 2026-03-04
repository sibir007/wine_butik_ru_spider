from pathlib import Path

import scrapy
from scrapy.http import Response


class WinesSpider(scrapy.Spider):
    name = "wines"

    async def start(self):
        urls = [
            "https://wine-butik.ru/wine/?limit=40&page=1",
            "https://wine-butik.ru/wine/?limit=40&page=2",
            "https://wine-butik.ru/wine/?limit=40&page=3",
            "https://wine-butik.ru/wine/?limit=40&page=4",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> None:
        page = response.url[-1]
        filename = f"wines-{page}.html"
        Path(filename).write_text(response.body.decode("cp1251"))
        self.log(f"Saved file {filename}")