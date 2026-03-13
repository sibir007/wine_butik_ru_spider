# https://wine-butik.ru/ скраппер 

# SRS 

Для сайта нужно реализовать Scrapy‑паука, который обходит сайт и собирает только карточки винных товаров.​
> выполнено в двух вариантах: на **Scrapy** и **Playwright**

Пауку необходимо:
1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
    > Выплнено. 
    ```py
   async def start(self) -> AsyncGenerator[Request, None]:
      # 1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
      # - начинаем с каталога            
      url = f"{self.wine_list_query.format('page=1')}"
      yield Request(url=url, callback=self.parse_cards_page)
    ```
2. Находить и переходить по всем (!) ссылкам на карточки винных товаров.
    > Выполнено 
    ```py
    def parse_cards_page(self, response: Response) -> Generator[Request, None, None]:
        # 2. Находить и переходить по всем (!) ссылкам на карточки винных товаров.
        # сформируем SelectorList всех винных карт на странице
        wine_cards: SelectorList = response.xpath(WINE_CARDS_XPATH)
        wine_cards_urls = (wine_card.xpath(WINE_HREFS_XPATH).get() for wine_card in wine_cards)
        # - выполним обход по страницам отдельных вин
        yield from response.follow_all(wine_cards_urls, callback=self.parse_wine_page)

    ```

3. Для каждой карточки вина формировать JSON‑объект со следующими полями:
    > Выполнено
    ```py
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
        # --- либо год не указан вообще
        vintage = vintage_1 or response.xpath(VINTAGE2_XPATH).get(default='').strip()

        # - наличие (в наличии / нет);
        # -- выдаётся в форме 'product-shop wait' или 'product-shop avail'
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
        yield Wine(
            name=name,
            vintage=vintage,
            availability=availability,
            image_url=image_url,
            price=Prise(price=price, currency=currency),
            volume=volume,
            order_size=order_size,
        )

    ```

4. Инструкция, как запустить паука и получить JSON‑выгрузку (README или описание в отклике).

Краткий комментарий, какие сложности встретились и как они решены (структура сайта, пагинация, фильтры и т.д.).