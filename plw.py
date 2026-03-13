from dataclasses import asdict
import json
from plw_util import Feed, JsonFeed, ParseCatalogPageResult, ParseWinePageResult, Prise, Wine, args
from playwright.async_api import BrowserContext, Locator, Response, async_playwright, Page, expect
from playwright.async_api import Error
import logging
import asyncio
from asyncio import Semaphore
from urllib.parse import urljoin
from http import HTTPStatus
import abc
from lxml import etree # type: ignore
from copy import deepcopy

from plw_util import (
    CatalogPageGoToResult, NavigationError, ParseResult, 
    ResponseError, ResultStatus, WineAtrrResoult, WinePageGoToResult, 
    get_availability_handle_result, get_currency_handle_result, 
    get_image_url_handle_result, get_name_handle_result, get_price_handle_result, 
    get_vintage_handle_result, get_volume_handle_result
    )

WINE_CARDS_XPATH = "//div[@class='catalog-item']"
WINE_HREFS_XPATH = ".//div[@class='catalog-item__desc']/h2/a[@href]" # /@href"
NEXT_PAGE_XPATH = "//div[@class='paging_box']/.//a[@class='next']" # /@value"

START_PAGE_URL = 'https://wine-butik.ru/'
XPATH_PREF = 'xpath={}'
FEED: Feed = JsonFeed()


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

async def crawl_wine_catalog_page(
        browser_context: BrowserContext, 
        semaphore: Semaphore, 
        wine_catalog_pag: Page
        ) -> ParseCatalogPageResult:
    wine_card_paths: list[str | None] = \
         [await l.get_attribute('href')
          for l in \
            await wine_catalog_pag.locator(XPATH_PREF.format(WINE_HREFS_XPATH)).all()]

    wine_card_urls: list[str] = [urljoin(wine_catalog_pag.url, p) for p in wine_card_paths if p is not None]

    parse_tacks_batch = [goto_wine_page(browser_context, url, wine_catalog_pag.url, semaphore) for url in wine_card_urls] 
    
    tack_batch_results = await asyncio.gather(*parse_tacks_batch)
                                                    

    # print(f'resoult len {len(tack_batch_results)}')
    return tack_batch_results


async def goto_wine_page(
        browser_context: BrowserContext, 
        page_url: str, 
        referer: str, 
        semaphore: Semaphore
        ) -> ParseWinePageResult :
    async with semaphore:
        page = await browser_context.new_page()
        try:
            response = await page.goto(page_url, referer=referer, wait_until='domcontentloaded')
            raise_err_response(page.url, response)
        except Error as e:
            page_goto_result = handle_page_goto_error(page.url, e)
            return (page_goto_result, None)
        else:
            page_goto_result = WinePageGoToResult()
        wine_atrr_resoults = await parse_wine_page(page)
    return page_goto_result, wine_atrr_resoults


async def parse_wine_page(page: Page) -> list[WineAtrrResoult]:
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
    name = await get_name_handle_result(page, parse_resoult)

    # - винтаж (год);
    vintage = await get_vintage_handle_result(page, parse_resoult)

    # - наличие (в наличии / нет);
    availability = await get_availability_handle_result(page, parse_resoult)

    # - URL основной картинки товара;
    image_url = await get_image_url_handle_result(page, parse_resoult)

    # - цена и валюта; price and currency
    price = await get_price_handle_result(page, parse_resoult)

    currency = await get_currency_handle_result(page, parse_resoult)

    # - объем бутылки (например, 375ml, 750ml, 1500ml);
    volume = await get_volume_handle_result(page, parse_resoult)

    # - количество бутылок (минимальный/стандартный размер заказа, если указано).
    # -- не указано на сайте
    order_size = ''

    
    # 3. Для каждой карточки вина формировать JSON‑объект со следующими полями: ...
    item = Wine(name, vintage, availability, image_url, Prise(price, currency), volume, order_size)
    # используемая имплементация FEED не требует записывать 'write()' данные в отдельном 
    # потоке, т.к. просто добавляет данные в проксированный list, сохранение данны
    # происходит при вызове метода 'close()' однако это может стать
    # удобно если мы захотим сделать имптементацию которая на каждый 'write()' будет делать
    # блокирующий вызов, например писать в csv файл - поэтому отправляем данные в экзекутор
    # FEED.write(item)
    # asyncio._get_running_loop().run_in_executor(None, FEED.write, item)
    FEED.write(item)
    await page.close()
    return parse_resoult

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

def store_resoutl(resoult, resoult_file: str):
    with open(resoult_file, 'w') as f:
        f.write(json.dumps(resoult, indent=2))


async def main(concurency: int, headless_mode: bool, prod_mod: bool, 
               feed_file :str, res_file: str):
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            # channel='chrome',
            headless=headless_mode,
            args=["--start-maximized", '--disable-blink-features=AutomationControlled']
        )

        browser_context = await browser.new_context(no_viewport=True)
        semaphore = Semaphore(concurency)
        FEED.open(feed_file)
        result = await start_crawl(browser_context, semaphore)
        result = handle_resoult2(result)
        asyncio.get_running_loop().run_in_executor(None, FEED.close)
        asyncio.get_running_loop().run_in_executor(None, store_resoutl, result, res_file)
        await browser.close()
    return result

if __name__ == '__main__':
    concurency, headless_mode, prod_mod, feed_file, res_file = args()
    asyncio.run(main(concurency, headless_mode, prod_mod, feed_file, res_file))
    