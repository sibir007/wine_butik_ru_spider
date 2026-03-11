from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from items import Prise, Wine # type: ignore
from util import ( # type: ignore
    WINE_NAME1_XPATH, WINE_NAME2_XPATH,VINTAGE1_XPATH, VINTAGE2_XPATH, AVAILABILITY_XPATH,
    IMG_URL_XPATH, PRICE_XPATH, CURRENCY_XPATH, VOLUME1_XPATH, VOLUME2_XPATH,
    availability_convert, image_url_conver, volume_convert
    ) 
from playwright.async_api import BrowserContext, Locator, Response, async_playwright, Page, expect
from playwright.async_api import Error
import logging
import asyncio
from asyncio import Semaphore
from urllib.parse import urljoin
from http import HTTPStatus
import abc
from lxml import etree # type: ignore

WINE_CARDS_XPATH = "//div[@class='catalog-item']"
WINE_HREFS_XPATH = ".//div[@class='catalog-item__desc']/h2/a[@href]" # /@href"
NEXT_PAGE_XPATH = "//div[@class='paging_box']/.//a[@class='next']" # /@value"

START_PAGE_URL = 'https://wine-butik.ru/'
XPATH_PREF = 'xpath={}'

type ParseWinePageResult = tuple[WinePageGoToResult, list[WineAtrrResoult] | None]
type ParseCatalogPageResult = list[ParseWinePageResult]


class Feed(abc.ABC):
    """ABC for feed"""

    abc.abstractmethod
    def open(self, file_name: str):
        """file name for store feed"""

    abc.abstractmethod
    def write(self, item: Wine):
        """write item to feed"""
    
    abc.abstractmethod
    def close(self):
        """close feed"""

FEED: Feed


class JsonFeed(Feed):

    def open(self, file_name: str):
        self.file_name = file_name
        self.feed: list[dict] = []
        return self

    def write(self, item: Wine):
        self.feed.append(asdict(item))
    
    def close(self):
        with open(self.file_name, 'w') as f:
            f.write(json.dumps(self.feed))


class ResultStatus(Enum):
    OK = True
    ERROR = False

@dataclass
class Resoult:
    status: bool = ResultStatus.OK.value
    page_url: str = ""

@dataclass
class WineAtrrResoult(Resoult):
    atrr_name: str = ""


@dataclass
class CatalogPageGoToResult(Resoult):
    err_type: str | None = None

@dataclass
class WinePageGoToResult(CatalogPageGoToResult):
    pass

@dataclass
class ParseResult:
    CatalogPageGoToResults: list[CatalogPageGoToResult] = field(default_factory=list) 
    WinePageGoToResults: list[WinePageGoToResult] = field(default_factory=list)
    WineAtrrResoults: list[WineAtrrResoult] = field(default_factory=list)


class NavigationError(Error):
    pass

class ResponseError(Error):
    pass

async def start_crawl(browser_context: BrowserContext, semaphore: Semaphore) -> ParseResult:
    parse_result = ParseResult()
    start_page_url = START_PAGE_URL

    page = await browser_context.new_page()
    
    # обрабатываем ошибки запроса
    try:
        response = await page.goto(start_page_url, timeout=60000)
        raise_err_response(page.url, response)
    except Error as e:
        # запиcываем ошибку в parse_result, пишем лог и выходм
        page_goto_err_result = handle_page_goto_error(start_page_url, e)
        parse_result.CatalogPageGoToResults.append(page_goto_err_result)
        return parse_result

    # подтверждаем возраст
    await page.locator("//span[contains(@class, 'button')]").click()
    # подтверждаем куки
    await page.locator("//button[contains(text(), 'Я согласен')]").click()
    # находим ссылку на каталог вин 
    catalog_page_locator: str = '#cat_330'
    wines_catalog_link_locator = page.locator(catalog_page_locator)
    # получим path что бы отследить загрузку каталога
    wines_catalog_link_path =  await wines_catalog_link_locator.get_attribute('href')
    # перейдём по ссылки для загрузки каталога вин
    try:
        await wines_catalog_link_locator.click()
        # дождёмся загрузки каталога        
        await page.wait_for_url(f'**{wines_catalog_link_path}', timeout=60000)

    except Error as e:
        # запиcываем ошибку в parse_result, пишем лог и выходм
        page_goto_err_result = handle_page_goto_error(page.url, e)
        parse_result.CatalogPageGoToResults.append(page_goto_err_result)
        return parse_result
    else:
        # запиcываем успех в parse_result
        parse_result.CatalogPageGoToResults.append(CatalogPageGoToResult())
    
    # парсим страницу каталога, получаем результат
    parse_catalog_page_result: ParseCatalogPageResult \
        = await crawl_wine_catalog_page(
            browser_context,
            semaphore,
            page
            )
    # записывем результат в результат парсинга
    for rez in parse_catalog_page_result:
        match rez:
            case (wine_page_goto_result, None):
                parse_result.WinePageGoToResults.append(wine_page_goto_result)
            case (wine_page_goto_result, pr):
                parse_result.WinePageGoToResults.append(wine_page_goto_result)
                parse_result.WineAtrrResoults.extend(pr)
            case _:
                logging.error(f'wrong programm state, parse resoult not match, result: {rez}')

    return parse_result

async def crawl_wine_catalog_page(browser_context: BrowserContext, semaphore: Semaphore, wine_catalog_pag: Page) -> ParseCatalogPageResult:
    wine_card_paths: list[str | None] = \
         [await l.get_attribute('href')
          for l in \
            await wine_catalog_pag.locator(XPATH_PREF.format(WINE_HREFS_XPATH)).all()]

    wine_card_urls: list[str] = [urljoin(wine_catalog_pag.url, p) for p in wine_card_paths if p is not None]

    parse_tacks_batch = [goto_wine_page(browser_context, url, wine_catalog_pag.url, semaphore) for url in wine_card_urls] 
    
    tack_batch_results = await asyncio.gather(*parse_tacks_batch)
                                                    

    # print(f'resoult len {len(tack_batch_results)}')
    return tack_batch_results


async def goto_wine_page(browser_context: BrowserContext, page_url: str, referer: str, semaphore: Semaphore) -> ParseWinePageResult :
    async with semaphore:
        page = await browser_context.new_page()
        try:
            response = await page.goto(page_url, referer=referer, timeout=60000)
            raise_err_response(page.url, response)
        except Error as e:
            page_goto_result = handle_page_goto_error(page.url, e)
            return (page_goto_result, None)
        else:
            page_goto_result = WinePageGoToResult()
        test_response = await response.text() # type: ignore
        wine_atrr_resoults = parse_wine_page(test_response, response.url) # type: ignore
        # await page.wait_for_timeout(5000)
        await page.close()
    return page_goto_result, wine_atrr_resoults
    # return page_goto_result, []


def parse_wine_page(response: str, page_url: str) -> list[WineAtrrResoult]:
    tree = etree.parse(response)
    parse_resoult: list[WineAtrrResoult] = []

    # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями:
    # - название вина;
    # - винтаж (год);
    # - наличие (в наличии / нет);
    # - URL основной картинки товара;
    # - цена и валюта;
    # - объем бутылки (например, 375ml, 750ml, 1500ml);
    # - количество бутылок (минимальный/стандартный размер заказа, если указано).
    
    # - название вина;
    name = tree.xpath(WINE_NAME1_XPATH).get(default='').strip()
    # -- если название не найдено, то попробуем найти его в другом месте
    name = name or tree.xpath(WINE_NAME2_XPATH).get(default='').strip()
    make_wine_atеr_resoult(page_url, parse_resoult, name, 'name')
    # - винтаж (год);
    # -- может выдаваться сервером в 3-х видах:
    # --- в виде контента selected option из списка возможных годов
    vintage_1 = tree.xpath(VINTAGE1_XPATH).get(default='').strip()
    # --- в виде контента p где потомок em содержит 'Год' и контент содержит сам год 
    # vintage_2 = response.xpath("//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]/../text()").get()
    # --- либо год не указан вообще
    vintage = vintage_1 or tree.xpath(VINTAGE2_XPATH).get(default='').strip()
    make_wine_atеr_resoult(page_url, parse_resoult, vintage, 'vintage')

    # - наличие (в наличии / нет);
    # -- выдаётся в форме 'product-shop wait' или 'product-shop avail'
    # -- обработку данных не стал выносить в Wine(Item) т.к. здесь удобнее это делать
    availability: str = tree.xpath(AVAILABILITY_XPATH).get(default='')
    availability = availability_convert(availability)
    make_wine_atеr_resoult(page_url, parse_resoult, vintage, 'vintage')

    # - URL основной картинки товара;
    image_url = tree.xpath(IMG_URL_XPATH).get(default='')
    # -- выдаётся в форме path+query (/uploads/products/new/45038.png?6172812833f175.12245300)
    image_url = image_url_conver(tree.url, image_url)
    make_wine_atеr_resoult(page_url, parse_resoult, image_url, 'image_url')

    # - цена и валюта; price and currency
    price = tree.xpath(PRICE_XPATH).get(default='')
    make_wine_atеr_resoult(page_url, parse_resoult, price, 'price')

    currency = tree.xpath(CURRENCY_XPATH).get(default='')
    make_wine_atеr_resoult(page_url, parse_resoult, currency, 'currency')

    # - объем бутылки (например, 375ml, 750ml, 1500ml);
    # -- выдаётся:
    # --- в виде контента p где потомок em содержит 'Объем' и контент содержит сам объём 
    volume_1 = tree.xpath(VOLUME1_XPATH).get(default='').strip()
    # --- в виде контента selected option из списка возможных объёмов
    volume = volume_1 or tree.xpath(VOLUME2_XPATH).get(default='').strip()
    # -- выдаётся в форме  '0.75 л'
    volume = volume_convert(volume)
    make_wine_atеr_resoult(page_url, parse_resoult, volume, 'volume')

    # - количество бутылок (минимальный/стандартный размер заказа, если указано).
    # -- не указано на сайте
    order_size = ''
    # не рассматриваем это значение как ошибку
    make_wine_atеr_resoult(page_url, parse_resoult, 'True', 'order_size')

    
    # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
    # - в Item обработки данных нет, поэтому можно было бы использовать dict,
    # - но т.к. он уже всё равно написан - сформируем запись из него

    item = Wine(
        name=name,
        vintage=vintage,
        availability=availability,
        image_url=image_url,
        price=Prise(price=price, currency=currency),
        volume=volume,
        order_size=order_size,
    )
    # используемая имплементация FEED не требует записывать 'write()' данные в отдельном 
    # потоке, т.к. просто добавляет данные в проксированный list, сохранение данны
    # происходит при вызове метода 'close()' однако это может стать
    # удобно если мы захотим сделать имптементацию которая на каждый 'write()' будет делать
    # блокирующий вызов, например писать в csv файл - поэтому отправляем данные в экзекутор
    # FEED.write(item)
    asyncio._get_running_loop().run_in_executor(None, FEED.write, item)

    return parse_resoult

def make_wine_atеr_resoult(page_url:str, parse_resoult: list[WineAtrrResoult], attr: str, attr_name: str):
    if attr:
        parse_resoult.append(WineAtrrResoult())
    else:
        parse_resoult.append(WineAtrrResoult(status=ResultStatus.ERROR.value, page_url=page_url, atrr_name=attr_name))

def raise_err_response(page_url: str, response: Response | None) -> None:
    if response is None:
        raise NavigationError(f'navigation to about:blank or navigation to the same URL, url: {page_url}')
    response_status = HTTPStatus(response.status)
    if not (response_status.is_success or response_status.is_redirection):
        raise ResponseError(f'response error, page_url: {page_url}, status: {response_status.description}')

def handle_page_goto_error(page_url:str, e: Error):
    logging.error(f'page go to error, url: {page_url}, err: {e}')
    result = CatalogPageGoToResult()
    result.status = ResultStatus.ERROR.value
    result.page_url = page_url
    result.err_type = e.__class__.__name__
    return result
    # pt = await page.title()
    
def handle_resoult(resoult: ParseResult) -> dict:
    res = asdict(resoult)
    # print(res)
    for r in res:
        res[r] = list(filter(lambda i: i['status'] == ResultStatus.ERROR.value, res[r]))
    return res

# для тестов
def handle_resoult2(resoult: ParseResult):
    res = asdict(resoult)
    return res

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            # channel='chrome',
            headless=False,
            args=["--start-maximized", '--disable-blink-features=AutomationControlled']
        )

        browser_context = await browser.new_context(no_viewport=True)
        semaphore = Semaphore(3)
        FEED = JsonFeed().open("rez.json")
        result = await start_crawl(browser_context, semaphore)
        result = handle_resoult2(result)
        # здесь блокирующий вызов
        await asyncio.get_running_loop().run_in_executor(None, FEED.close)
        await browser.close()
    return result

if __name__ == '__main__':
    res = asyncio.run(main())
    with open('parse_res.json', 'w') as f:
        f.write(json.dumps(res, indent=2))
