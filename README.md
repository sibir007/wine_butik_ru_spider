# https://wine-butik.ru/ скраппер 

# SRS 

Для сайта нужно реализовать Scrapy‑паука, который обходит сайт и собирает только карточки винных товаров.​
> выполнено в двух вариантах: на **Scrapy** и **Playwright**

Пауку необходимо:
1. Начинать обход с главной страницы, каталога или sitemap (на твой выбор).
    > Выплнено. 
    ```py
   wine_list_query = "https://wine-butik.ru/wine/?limit=40&{}"

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
   ```bash
   # клонируем репозиторий
   sibir007@sibir007:~/repos$ git clone https://github.com/sibir007/wine_butik_ru_spider.git wine_parser_doble
   # заходм в дирректорию проекта
   sibir007@sibir007:~/repos$ cd wine_parser_doble
   # создаём и активируем окружение
   sibir007@sibir007:~/repos/wine_parser_doble$ python3 -m venv .venv
   sibir007@sibir007:~/repos/wine_parser_doble$ . .venv/bin/activate
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ 
   # устанавливаем зависимости
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ pip install -r requirements.txt 
   Collecting Scrapy==2.14.1 (from -r requirements.txt (line 1))
     Using cached scrapy-2.14.1-py3-none-any.whl.metadata (4.3 kB)
   Collecting pytest-playwright==0.7.2 (from -r requirements.txt (line 2))
   ...
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ 
   # установка браузеров для playwright
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ playwright install
   # запускаем спайдера. 
   # По уполчанию будет 1 конкурирущий запрос в секунду (т.е. будет долго) и максимум 7 страниц каталога будет обойдено (всё равно долго), ответы сохраняться в кэше и последующие вызовы будут братьcя из кэша (т.е. буде бытро) - менять настройками и аргументами командной строки (ниже). 
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ scrapy crawl wines -o feed.json 
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ ls -la feed.json 
   -rw-rw-r-- 1 sibir007 sibir007 77310 Mar 13 20:05 feed.json
   (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ cat feed.json
   [
   {"name": "Фюг Де Ненан Помроль", "vintage": "2017", "availability": "avail", "image_url": "https://wine-butik.ru/uploads/products/new/44956.png", "price": {"price": "5600", "currency": "RUB"}, "volume": "750ml", "order_size": ""},
   {"name": "Кумала Медиум Свит Уайт", "vintage": "", "availability": "wait", "image_url": "https://wine-butik.ru/uploads/products/new/33989.png", "price": {"price": "360", "currency": "RUB"}, "volume": "750ml", "order_size": ""},
   {"name": "Вальжан", "vintage": "", "availability": "wait", "image_url": "https://wine-butik.ru/uploads/products/new/42977.png", "price": {"price": "460", "currency": "RUB"}, "volume": "750ml", "order_size": ""},
   ...
   ```
5. Краткий комментарий, какие сложности встретились и как они решены 
    - были ошибки при большом колличесве конкурирующих запростов, поэтому настройки для разрабоки установлены:
      ```py
      CONCURRENT_REQUESTS = 1
      DOWNLOAD_DELAY = 2
      RANDOMIZE_DOWNLOAD_DELAY = True
      CONCURRENT_REQUESTS_PER_DOMAIN = 1
      CACHE_ENABLED = True
      HTTPCACHE_EXPIRATION_SECS = 0
      ```
      также спайдер принимает аргументы из коммандной строки:
      ```py
      def __init__(self, dev: bool = True, dpc: str = '7', *args, **kwargs: Any):
          """_summary_

          Args:
              dev (bool, optional): set development mode. Defaults to True.
              dpc (str, optional): count page to crawl in dev mod. Defaults to 7.
          """
      ```
      т.е. по умолчанию девелопмент мод в котором по умолчанию производится обход 7 (dpc) страниц каталога, если `dev == False`, то колличество страниц не учитывается.
    - сайт в кодировке windows-1251, поэтому feed сохранялся не правильно, устранено настройкой:
      ```py
      FEED_EXPORT_ENCODING = "utf-8"
      ```
(.venv) sibir007@sibir007:~/repos/wine_parser_doble$ uname -a
Linux sibir007 6.17.0-14-generic #14~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Jan 15 15:52:10 UTC 2 x86_64 x86_64 x86_64 GNU/Linux

# Playwright implementation

- зависимости установлены при установке ранее, однако могут потребоваться дополнительно устанавовить в зависимости от системы на которой производится запуск, подробнее https://playwright.dev/python/docs/intro#installing-playwright-pytest
- в демо версии скрапер парсит только одну страницу каталога
- скрапер принимает опцональные параметры:
  ```bash
  (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ python3 plw.py -h
    usage: plw.py [-h] [-c CONCURENCY] [-l] [-p] [-f FEED] [-r RES]

    options:
      -h, --help            show this help message and exit
      -c CONCURENCY, --concurency CONCURENCY
                            Count of concurrently opened and parsed wine pages
      -l, --less            Headless mode. If -l pointed - borowser run in headless mode. Default headless=False
      -p, --prod            Prodaction mod. If -p not pointed (i.e. set dev mod) - parsed only one catalog page.
      -f FEED, --feed FEED  Feed output file. Default feed.json
      -r RES, --res RES     Parse resoults output file. Default resoult.json
  ```
    - `-c` колличество конкурирующих запросов: скрапер одновременно отрывает несколько окон браузера со страницами вин и параллельно (конкурентно) парсит их, по умолчанию открывает 3
    - `-l` по умолчанию браузет запустится не headless режиме
    - `-p` продакшен режим не реализован, спарсится только одна страница каталога
    - `-f` оутпут файл для feed
    - `-r`оутпут файл для статистики парсинга
- запуск
  ```bash
  # будет парсить по 10 страниц одновременно
  (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ python3 plw.py -c 10
  ```
  ![adminer](Screenshot%20from%202026-03-13%2021-15-24.png)

  ```bash
  (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ cat feed.json 
  [
  {
    "name": "Сангре де Торо Розовое 0.0.",
    "vintage": "2020",
    "availability": "avail",
    "image_url": "https://wine-butik.ru/uploads/products/new/44679.png",
    "price": {
      "price": "930",
      "currency": "RUB"
    },
    "volume": "750ml",
    "order_size": ""
  },
  ...

  (.venv) sibir007@sibir007:~/repos/wine_parser_doble$ cat resoult.json 
    {
      "catalog_page_crawl_count": 1,
      "catalog_page_crawl_errot_count": 0,
      "wine_page_crawl_count": 20,
      "wine_page_crawl_errot_count": 0,
      "wine_attr_parsing_count": 140,
      "wine_attr_parsing_errot_count": 4,
      "catalog_page_crawl_error_results": [],
      "wine_page_crawl_error_results": [],
      "wine_attr_parsing_error_results": [
        {
          "status": false,
          "page_url": "https://wine-butik.ru/nonalco_sweet_white_sparkling/klaus-langhoff-whitewine-alcoholfree/",
          "err_type": [
            "TimeoutError --- Locator.text_content: Timeout 5000ms exceeded.\nCall log:\n  - waiting for locator(\"//div[contains(@class, 'prod_param_2')]/.//option[@selected]\")\n --- xpath=//div[contains(@class, 'prod_param_2')]/.//option[@selected]",
            "TimeoutError --- Locator.text_content: Timeout 5000ms exceeded.\nCall log:\n  - waiting for locator(\"//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]\").locator(\"..\")\n --- xpath=//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]"
          ],
          "atrr_name": "vintage"
        },
        {
          "status": false,
          "page_url": "https://wine-butik.ru/dry_red/muelle-tempranillo-syrah-tierra-de-castilla-igp/",
          "err_type": [
          
  ```