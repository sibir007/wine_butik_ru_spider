from collections.abc import AsyncGenerator, Coroutine, Generator
from dataclasses import dataclass, field
from enum import Enum
import functools
import re
from typing import Iterable
from items import Wine
from playwright.async_api import BrowserContext, Locator, Response, async_playwright, Page, expect
from playwright.async_api import TimeoutError, Error
# from wine_butik_ru_spider.items import Wine, Prise
import logging
import asyncio
from asyncio import Semaphore

from urllib.parse import urljoin
from http import HTTPStatus


WINE_CARDS_XPATH = "//div[@class='catalog-item']"
WINE_HREFS_XPATH = ".//div[@class='catalog-item__desc']/h2/a[@href]" # /@href"
NEXT_PAGE_XPATH = "//div[@class='paging_box']/.//a[@class='next']" # /@value"
WINE_NAME1_XPATH = "//div[contains(@class, 'product-translation')]/span" # /text()[normalize-space()]"
WINE_NAME2_XPATH = "//div[contains(@class, 'product-title')]/h1" # /text()[normalize-space()]"
VINTAGE2_XPATH = "//div[contains(@class, 'prod_param_2')]/p/em/[contains(text(), 'Год')]/../p" # /text()"
AVAILABILITY_XPATH = "//div[contains(@class, 'product-shop wait')]/@class | //div[contains(@class, 'product-shop avail')]" # /@class"
IMG_URL_XPATH = "//img[contains(@class, 'product-image-large')]" # /@src"
PRICE_XPATH = "//div[contains(@id, 'product-price')]/div[2]" # /text()"
CURRENCY_XPATH = "//div[contains(@id, 'product-price')]/div[3]" # /text()"
VOLUME1_XPATH = "//div[@class='product-params']/p/em[contains(text(), 'Объем')]/.." # /text()"
VOLUME2_XPATH = "//div[@class='product-params']/p/em[contains(text(), 'Объем')]/..//option[@selected]" # /text()"


# page = 'https://playwright.dev/'
start_page = 'https://wine-butik.ru/'
XPATH_PREF = 'xpath={}'

type ParseWinePageResult = tuple[WinePageGoToResult, ParseResult | None]
type ParseCatalogPageResult = list[ParseWinePageResult]

FEED: list[Wine]  = []
        

class PageGoToStatus(Enum):
    OK = 'OK'
    ERROR = 'ERROR'


@dataclass
class WineAtrrResoult:
    atrr_name: str
    result: bool = True

@dataclass
class WinePageResult:
    page_url: str
    result: bool = True
    err_type: Error | TimeoutError | None = None
    err_atrr_results: list[WineAtrrResoult] = field(default_factory=list)


@dataclass
class CatalogPageGoToResult:
    result: PageGoToStatus = PageGoToStatus.OK
    page_url: str = ''
    err_type: type[Error] | None = None

@dataclass
class WinePageGoToResult(CatalogPageGoToResult):
    pass

@dataclass
class ParseResult:
    CatalogPageGoToResults: list[CatalogPageGoToResult] = field(default_factory=list) 
    WinePageGoToResults: list[WinePageGoToResult] = field(default_factory=list)

class NavigationError(Error):
    pass

class ResponseError(Error):
    pass

async def start_cawl(browser_context: BrowserContext, semaphore: Semaphore):
    parse_result = ParseResult()
    start_page_url = 'https://wine-butik.ru/'

    page = await browser_context.new_page()
    # xp = 'xpath={}'
    
    try:
        response = await page.goto(start_page_url)
        handle_response(page.url, response)
        # response.s
    except Error as e:
        page_goto_err_result = handle_page_goto_error(start_page_url, e)
        parse_result.CatalogPageGoToResults.append(page_goto_err_result)
        return parse_result

    # подтверждаем возраст
    await page.locator("//span[contains(@class, 'button')]").click()
    # подтверждаем куки
    await page.locator("//button[contains(text(), 'Я согласен')]").click()
    # находим ссылку на каталог вин 
    wines_catalog_link_locator = page.locator('#cat_330')
    # получим path что бы отследить загрузку каталога
    wines_catalog_link_path =  await wines_catalog_link_locator.get_attribute('href')
    print(wines_catalog_link_path)
    # перейдём по ссылки для загрузки каталога вин
    try:
        await wines_catalog_link_locator.click()
        # дождёмся загрузки каталога        
        await page.wait_for_url(f'**{wines_catalog_link_path}')

    except Error as e:
        page_goto_err_result = handle_page_goto_error(page.url, e)
        parse_result.CatalogPageGoToResults.append(page_goto_err_result)
        return parse_result
    else:
        parse_result.CatalogPageGoToResults.append(WinePageGoToResult(page_url=page.url))
    parse_catalog_gage_result: ParseCatalogPageResult \
        = await crawl_wine_catalog_page(
            browser_context,
            semaphore,
            page
            )
    

async def crawl_wine_catalog_page(browser_context: BrowserContext, semaphore: Semaphore, wine_catalog_pag: Page) -> ParseCatalogPageResult:
    wine_card_paths: list[str | None] =  [await l.get_attribute('href') 
                                                  for l 
                                                  in await wine_catalog_pag.locator(XPATH_PREF.format(WINE_HREFS_XPATH)).all()]

    wine_card_urls: list[str] = [urljoin(wine_catalog_pag.url, p) for p in wine_card_paths if p is not None]

    parse_tacks_batch = [goto_wine_page(browser_context, url, wine_catalog_pag.url, semaphore) for url in wine_card_urls] 
    
    tack_batch_results = await asyncio.gather(*parse_tacks_batch)
                                                    

    print(f'resoult len {len(tack_batch_results)}')
    return tack_batch_results


async def goto_wine_page(browser_context: BrowserContext, page_url: str, referer: str, semaphore: Semaphore) -> ParseWinePageResult :
    async with semaphore:
        page = await browser_context.new_page()
        try:
            response = await page.goto(page_url, referer=referer)
            handle_response(page.url, response)
        except Error as e:
            page_goto_result = handle_page_goto_error(page.url, e)
            return (page_goto_result, None)
        else:
            page_goto_result = WinePageGoToResult(page_url=page.url)
        await page.wait_for_timeout(5000)
        await page.close()
    return True


def handle_response(page_url: str, response: Response | None):
    if response is None:
        raise NavigationError(f'navigation to about:blank or navigation to the same URL, url: {page_url}')
    response_status = HTTPStatus(response.status)
    if not (response_status.is_success or response_status.is_redirection):
        raise ResponseError(f'response error, page_url: {page_url}, status: {response_status.description}')

def handle_page_goto_error(page_url:str, e: Error):
    logging.error(f'page go to error, url: {page_url}, err: {e}')
    result = CatalogPageGoToResult()
    result.result = PageGoToStatus.ERROR
    result.page_url = page_url
    result.err_type = type(e)
    return result
    # pt = await page.title()
    

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            # channel='chrome',
            headless=False,
            args=["--start-maximized", '--disable-blink-features=AutomationControlled']
        )

        browser_context = await browser.new_context(no_viewport=True)
        semaphore = Semaphore(3)
        await start_cawl(browser_context, semaphore)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
