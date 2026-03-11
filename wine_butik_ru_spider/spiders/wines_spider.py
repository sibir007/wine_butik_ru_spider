# from collections.abc import Iterator
from collections.abc import Generator, AsyncGenerator
import logging
from pathlib import Path
from typing import Any, cast

from parsel import SelectorList
import scrapy
from scrapy.http import Response, Request, HtmlResponse
from urllib import parse
from wine_butik_ru_spider.plw import parse_wine_catalog
import asyncio

# from scrapy import 

from wine_butik_ru_spider.items import Wine, Prise
from wine_butik_ru_spider.util import AVAILABILITY_XPATH, CURRENCY_XPATH, IMG_URL_XPATH, NEXT_PAGE_XPATH, PRICE_XPATH, VINTAGE1_XPATH, VINTAGE2_XPATH, VOLUME1_XPATH, VOLUME2_XPATH, WINE_CARDS_XPATH, WINE_HREFS_XPATH, WINE_NAME1_XPATH, WINE_NAME2_XPATH, availability_convert, image_url_conver, volume_convert


class WinesSpider(scrapy.Spider):
    name = "wines"
    wine_list_query = "https://wine-butik.ru/wine/?limit=40&{}"

    # def __init__(self, **kwargs: Any):
    def __init__(self, dev: bool = True, dpc: str = '7', *args, **kwargs: Any):
        """_summary_

        Args:
            dev (bool, optional): set development mode. Defaults to True.
            dpc (str, optional): count page to crawl in dev mod. Defaults to 7.
        """
        # установим максимальное колличесто сраниц для обхода
        if dev:
            self.DEV_MODE = True
            try:
                self.pages_count = int(dpc)
            except ValueError as e:
                self.log(f'wrong value for dpc: {dpc}, error: {e}', level=logging.ERROR)
                self.pages_count = 7
        super().__init__(*args, **kwargs)

    async def start(self) -> AsyncGenerator[Request, None]:


        # 1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
        # - начинаем с каталога            
        url = f"{self.wine_list_query.format('page=1')}"
        # title = await get_page_title('https://playwright.dev/')
        # print('-'*20 + f'-> title: {title}')
        # yield Request(url=url, callback=self.test_callback)
        yield Request(url=url, callback=self.parse_cards_page)


    def test_callback(self, response: Response)-> None:
        Path('test.html').write_bytes(response.body)


    def follow_all_links(self, wine_cards: SelectorList, response: Response) -> Generator[Request, None, None]:
        
        # т.к. задача не несёт функциональной нагрузки, для уменьшения нагрузки на сервер - упростим её
        # 1. получим сразу все ссылки по картам
        wine_cards_urls = wine_cards.xpath(".//@href").getall()
        
        # 2. оставим уникальные
        wine_cards_urls_set = set(wine_cards_urls)
        
        # 3. выполним обход
        def empty_callback(response: Response) -> Generator[None, None, None]:
            yield None
        yield from response.follow_all(wine_cards_urls_set, callback=empty_callback)


    def parse_cards_page(self, response: Response) -> Generator[Request, None, None]:

        response = cast(HtmlResponse, response)
        
        # сформируем SelectorList всех винных карт на странице
        
        wine_cards: SelectorList = response.xpath(WINE_CARDS_XPATH)

        # 2. Находить и переходить по всем (!) ссылкам на карточки винных товаров.
        # - задача без функциональной нагрузки, выделим в отдельный метод
        # - сделаем доступным только в DEV резиме
        # if self.DEV_MODE:
        #     yield from self.follow_all_links(wine_cards, response)
        
        # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
        # хотя в каждой карте из каталога достаточно информаии для создания объекта,
        # перейдём на страницу вина и возьмём всю информацию оттуда, для этого:
        # - получим ссылки на страницы вин из винных карточек

        wine_cards_urls = (wine_card.xpath(WINE_HREFS_XPATH).get() for wine_card in wine_cards)
        # - выполним обход по страницам отдельных вин
        yield from response.follow_all(wine_cards_urls, callback=self.parse_wine_page)

        # - выполним проверку наличия следущей страницы каталога
        # - //div[@class='paging_box']/.//a[@class='next']/@value
        next_page = response.xpath(NEXT_PAGE_XPATH).get(default='').strip()
        if next_page:
            # для DEV режима считаем колличиесто обойдённых страниц каталога
            if self.DEV_MODE:
                if not self.pages_count:
                    return None
                self.pages_count -= 1
            yield Request(url=self.wine_list_query.format(next_page), callback=self.parse_cards_page)




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
        name = response.xpath(WINE_NAME1_XPATH).get(default='').strip()
        # -- если название не найдено, то попробуем найти его в другом месте
        name = name or response.xpath(WINE_NAME2_XPATH).get(default='').strip()
        # - винтаж (год);
        # -- может выдаваться сервером в 3-х видах:
        # --- в виде контента selected option из списка возможных годов
        vintage_1 = response.xpath(VINTAGE1_XPATH).get(default='').strip()
        # --- в виде контента p где потомок em содержит 'Год' и контент содержит сам год 
        # vintage_2 = response.xpath("//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]/../text()").get()
        # --- либо год не указан вообще
        vintage = vintage_1 or response.xpath(VINTAGE2_XPATH).get(default='').strip()

        # - наличие (в наличии / нет);
        # -- выдаётся в форме 'product-shop wait' или 'product-shop avail'
        # -- обработку данных не стал выносить в Wine(Item) т.к. здесь удобнее это делать
        availability: str = response.xpath(AVAILABILITY_XPATH).get(default='')
        availability = availability_convert(availability)

        # - URL основной картинки товара;
        image_url = response.xpath(IMG_URL_XPATH).get(default='')
        # -- выдаётся в форме path+query (/uploads/products/new/45038.png?6172812833f175.12245300)
        image_url = image_url_conver(response.url, image_url)

        # - цена и валюта; price and currency
        price = response.xpath(PRICE_XPATH).get(default='')
        currency = response.xpath(CURRENCY_XPATH).get(default='')

        # - объем бутылки (например, 375ml, 750ml, 1500ml);
        # -- выдаётся:
        # --- в виде контента p где потомок em содержит 'Объем' и контент содержит сам объём 
        volume_1 = response.xpath(VOLUME1_XPATH).get(default='').strip()
        # --- в виде контента selected option из списка возможных объёмов
        volume = volume_1 or response.xpath(VOLUME2_XPATH).get(default='').strip()
        # -- выдаётся в форме  '0.75 л'
        # -- обработку оставил здесь т.к. удобнее
        volume = volume_convert(volume)

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
            order_size=order_size,
        )
        
        if False:
            yield Wine(
                name=name,
                vintage=vintage,
                availability=availability,
                image_url=image_url,
                price=Prise(price=price, currency=currency),
                volume=volume,
                order_size=order_size,
                url = response.url
            )




