# from collections.abc import Iterator
from collections.abc import Generator, AsyncGenerator
import logging
from typing import cast

from parsel import SelectorList
import scrapy
from scrapy.http import Response, Request, HtmlResponse
from urllib import parse

from wine_butik_ru_spider.items import Wine, Prise


class WinesSpider(scrapy.Spider):
    name = "wines"
    wine_list_query = "https://wine-butik.ru/wine/?limit=40&{}"

    async def start(self) -> AsyncGenerator[Request, None]:

        # 1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
        # - начинаем с каталога            
        url = f"{self.wine_list_query.format('page=131')}"
        # yield Request(url=url, callback=self.test_callback)
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

        response = cast(HtmlResponse, response)
        
        # сформируем SelectorList всех винных карт на странице
        wine_cards: SelectorList = response.xpath("//div[@class='catalog-item']")

        # 2. Находить и переходить по всем (!) ссылкам на карточки винных товаров.
        # - задача без функциональной нагрузки, выделим в отдельный метод
        # yield from self.follow_all_links(wine_cards, response)
        
        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
        # хотя в каждой карте из каталога достаточно информаии для создания объекта,
        # перейдём на страницу вина и возьмём всю информацию оттуда, для этого:
        # - получим ссылки на страницы вин из винных карточек
        wine_cards_urls = (wine_card.xpath(".//div[@class='catalog-item__desc']/h2/a[@href]/@href").get() for wine_card in wine_cards)
        # - выполним обход по страницам отдельных вин
        # wine_cards_urls = list(wine_cards_urls)
        # print(len(wine_cards_urls))
        yield from response.follow_all(wine_cards_urls, callback=self.parse_wine_page)


    def parse_wine_page(self, response: Response) -> Generator[Wine, None, None]:

        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями:
        # - название вина;
        # - винтаж (год);
        # - наличие (в наличии / нет);
        # - URL основной картинки товара;
        # - цена и валюта;
        # - объем бутылки (например, 375ml, 750ml, 1500ml);
        # - количество бутылок (минимальный/стандартный размер заказа, если указано).
        
        # - название вина;
        name = response.xpath("//div[contains(@class, 'product-translation')]/span[normalize-space()]/text()").get(default='')

        # - винтаж (год);
        # -- может выдаваться сервером в 3-х видах:
        # --- в виде контента selected option из списка возможных годов
        vintage_1 = response.xpath("//div[contains(@class, 'prod_param_2')]/.//option[@selected]/text()").get(default='').strip()
        # --- в виде контента p где потомок em содержит 'Год' и контент содержит сам год 
        # vintage_2 = response.xpath("//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]/../text()").get()
        # --- либо год не указан вообще
        vintage = vintage_1 or response.xpath("//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]/../text()").get(default='').strip()

        # - наличие (в наличии / нет);
        # -- выдаётся в форме 'product-shop wait' или 'product-shop avail'
        # -- обработку данных не стал выносить в Wine(Item) т.к. здесь удобнее это делать
        availability = response.xpath("//div[contains(@class, 'product-shop wait')]/@class | //div[contains(@class, 'product-shop avail')]/@class").get(default='')
        match availability.split():
            case [_, a]:
                availability = a
            case _:
                self.log(f'unrecognized value of availability: {availability}', level=logging.ERROR)
                availability = ''

        # - URL основной картинки товара;
        image_url = response.xpath("//img[contains(@class, 'product-image-large')]/@src").get(default='')
        # -- выдаётся в форме path+query (/uploads/products/new/45038.png?6172812833f175.12245300)
        if image_url:
            # -- выделим path
            path = parse.urlparse(image_url).path
            # -- построим url
            image_url = parse.urlparse(response.url)._replace(path=path, query='', fragment='').geturl()

        # - цена и валюта; price and currency
        price = response.xpath("//div[contains(@id, 'product-price')]/div[2]/text()").get(default='')
        currency = response.xpath("//div[contains(@id, 'product-price')]/div[3]/text()").get(default='')

        # - объем бутылки (например, 375ml, 750ml, 1500ml);
        # -- выдаётся:
        # --- в виде контента p где потомок em содержит 'Объем' и контент содержит сам объём 
        volume_1 = response.xpath("//div[@class='product-params']/p/em[contains(text(), 'Объем')]/../text()").get(default='').strip()
        # --- в виде контента selected option из списка возможных объёмов
        volume = volume_1 or response.xpath("//div[@class='product-params']/p/em[contains(text(), 'Объем')]/..//option[@selected]/text()").get(default='').strip()
        # -- выдаётся в форме  '0.75 л'
        # -- обработку оставил здесь т.к. удобнее
        match volume.split():
            case [v, _]:
                try:
                    volume = str(int(float(v)*1000)) + 'ml'
                except ValueError as e:
                    self.log(e, level=logging.ERROR)
                    volume = ''
            case _:
                self.log(f'unrecognized value of volume: {volume}', level=logging.ERROR)
                volume = ''

        # - количество бутылок (минимальный/стандартный размер заказа, если указано).
        # -- не указано на сайте
        order_size = ''
        
        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
        # - в Item обработки данных нет, поэтому можно было бы использовать dict,
        # - но т.к. он уже всё равно написан - сформируем запись из него
        yield Wine(
            name=name,
            vintage=vintage,
            availability=availability,
            image_url=image_url,
            price=Prise(price=price, currency=currency),
            volume=volume,
            order_size=order_size
        )
        