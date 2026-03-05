# from collections.abc import Iterator
from collections.abc import Generator
from pathlib import Path
from tarfile import LENGTH_LINK
from typing import Iterable, AsyncGenerator

from parsel import Selector, SelectorList
import scrapy
from scrapy.http import Response, Request


class WinesSpider(scrapy.Spider):
    name = "wines"
    wine_list_query = "https://wine-butik.ru/wine/?limit=40&{}"

    async def start(self) -> AsyncGenerator[Request, None]:

        # 1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
        # - начинаем с каталога            
        url = f"{self.wine_list_query.format('page=1')}"
        yield Request(url=url, callback=self.parse_cards_page)
    

    def follow_all_links(self, wine_cards: SelectorList, response: Response) -> Generator[Request, None, None]:
        
        # т.к. задача не несёт функциональной нагрузки, для уменьшения нагрузки на сервер - упростим её
        # 1. получим сразу все ссылки по картам
        wine_cards_urls = wine_cards.xpath(".//@href").getall()
        
        # 2. оставим уникальные
        wine_cards_urls_set = set(wine_cards_urls)
        
        # 3. выполним обход
        def empty_callback(response: Response) -> None:
            return None
        yield from response.follow_all(wine_cards_urls_set, callback=empty_callback)


    def parse_cards_page(self, response: Response) -> Generator[Request, None, None]:
        base_url = self.settings.get("BASE_URL")

        # сформируем SelectorList всех винных карт на странице
        wine_cards: SelectorList = response.xpath("//div[@class='catalog-item']")

        # 2. Находить и переходить по всем (!) ссылкам на карточки винных товаров.
        # - задача без функциональной нагрузки, выделим в отдельный метод
        yield from self.follow_all_links(wine_cards, response)
        
        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
        # хотя в каждой карте из каталога достаточно информаии для создания объекта,
        # перейдём на страницу вина и возьмём всю информацию оттуда, для этого:
        # - получим ссылки на страницы вин из винных карточек
        wine_cards_urls = (wine_card.xpath(".//div[@class='catalog-item__desc']/h2/a[@href]/@href").get() for wine_card in wine_cards)
        # - выполним обход по страницам отдельных вин
        yield from response.follow_all(wine_cards_urls, callback=self.parse_wine_page)


    def parse_wine_page(self, response: Response) -> Generator[Request, None, None]:

        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями:
        # - название вина;
        # - винтаж (год);
        # - наличие (в наличии / нет);
        # - URL основной картинки товара;
        # - цена и валюта;
        # - объем бутылки (например, 375ml, 750ml, 1500ml);
        # - количество бутылок (минимальный/стандартный размер заказа, если указано).

        yield  None          


"""
//div[@class='product-params prod_param_2']//select//option/@href
div.product-params.prod_param_2 select.product-params-select option
class Prise(Item):
    price = Field(
        input_processor=MapCompose(partial(float_checker, 2))
        )
    currency = Field()


class Wine(Item):
    name = Field()
    vintage = Field(
        input_processor=MapCompose(int_checker)
        )
    availability = Field()
    image_url = Field()
    price = Field()
    bottle_volume = Field(
        input_processor=MapCompose(partial(float_checker, 3))
        )
    bottle_count = Field(
        input_processor=MapCompose(int_checker)
        )

"""