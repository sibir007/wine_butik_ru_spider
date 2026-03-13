import abc
import argparse
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from urllib import parse
from playwright.async_api import async_playwright, Page
from playwright.async_api import Error
import logging
import asyncio
from urllib.parse import urljoin


class ResultStatus(Enum):
    OK = True
    ERROR = False

@dataclass
class Resoult:
    status: bool = ResultStatus.OK.value
    page_url: str = ""

@dataclass
class CatalogPageGoToResult(Resoult):
    err_type: str | None = None

@dataclass
class WinePageGoToResult(CatalogPageGoToResult):
    pass

@dataclass
class WineAtrrResoult(CatalogPageGoToResult):
    atrr_name: str = ""

@dataclass
class ParseResult:
    CatalogPageGoToResults: list[CatalogPageGoToResult] = field(default_factory=list) 
    WinePageGoToResults: list[WinePageGoToResult] = field(default_factory=list)
    WineAtrrResoults: list[WineAtrrResoult] = field(default_factory=list)

@dataclass
class Prise:
    price: str
    currency: str

@dataclass
class Wine:
    name: str
    vintage: str
    availability: str
    image_url: str
    price: Prise
    volume: str
    order_size: str


class NavigationError(Error):
    pass

class ResponseError(Error):
    pass



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




async def test_main() -> list[WineAtrrResoult]:
    test_urls = [
        "https://wine-butik.ru/error",
        "https://wine-butik.ru/nonalco_sweet_white_sparkling/klaus-langhoff-whitewine-alcoholfree/",
        'https://wine-butik.ru/dry_red/paul-mas-pinot-noir-pays-d-oc-igp-2020/', 
        "https://wine-butik.ru/dry_red/chateau-cheval-blanc-premier-grand-cru-classe-a-saint-emilion-grand-cru-aoc-1996/"
        ]
    parse_resoult: list[WineAtrrResoult] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            # channel='chrome',
            headless=False,
            args=["--start-maximized", '--disable-blink-features=AutomationControlled']
        )

        browser_context = await browser.new_context(no_viewport=True)

        page = await browser_context.new_page()
        for url in test_urls:
            response = await page.goto(url, wait_until='domcontentloaded')
            page.set_default_timeout(timeout=10000)
            res = await get_volume_handle_result(page, parse_resoult)
            # res = await get_currency_handle_result(page, parse_resoult)
            # res = await get_price_handle_result(page, parse_resoult)
            # res = await get_image_url_handle_result(page, parse_resoult)
            # res = await get_availability_handle_result(page, parse_resoult)
            # res = await get_vintage_handle_result(page, parse_resoult)
            # res = await get_name_handle_result(page, parse_resoult)
            print(res)
        
        print(parse_resoult)
        
        await browser.close()

    return parse_resoult


async def get_volume_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        volume1_xpath = "xpath=//div[@class='product-params']/p/em[contains(text(), 'Объем')]/..//option[@selected]"
        volume = await page.locator(volume1_xpath).text_content()
        volume = volume or ''
    except Error as e1:
        try:
            volume2_xpath = "xpath=//div[@class='product-params']/p/em[contains(text(), 'Объем')]"
            volume =  await page.locator(volume2_xpath).locator("..").text_content()
            volume = volume or ''
        except Error as e2:
            volume = ''
            make_wine_atter_resoult(parse_resoult, page.url, 'volume', [(e1, volume1_xpath), (e2, volume2_xpath)])
        else:
            make_wine_atter_resoult(parse_resoult)
    else:
        make_wine_atter_resoult(parse_resoult)

    match volume.split():
        case [_, v, _] | [v, _]:
            try:
                volume = str(int(float(v)*1000)) + 'ml'
            except ValueError as e:
                logging.log(msg=e, level=logging.ERROR)
                volume = ''
        case _:
            logging.log(msg=f'unrecognized value of volume: {volume}, url: {page.url}', level=logging.ERROR)
            volume = ''

    return volume


async def get_currency_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        currency_xpath = "//div[contains(@id, 'product-price')]/div[3]"
        currency = await page.locator(currency_xpath).text_content()
        currency = currency or ''
    except Error as e1:
        currency = ''
        make_wine_atter_resoult(parse_resoult, page.url, 'currency', [(e1, currency_xpath)])
    else:
        make_wine_atter_resoult(parse_resoult)

    return currency



async def get_price_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        price_xpath = "//div[contains(@id, 'product-price')]/div[2]"
        price = await page.locator(price_xpath).text_content()
        price = price or ''
    except Error as e1:
        price = ''
        make_wine_atter_resoult(parse_resoult, page.url, 'price', [(e1, price_xpath)])
    else:
        make_wine_atter_resoult(parse_resoult)

    return price

async def get_image_url_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        image_url_xpath = "//img[contains(@class, 'product-image-large')]"
        image_url = await page.locator(image_url_xpath).get_attribute('src')
        image_url = image_url or ''
    except Error as e1:
        image_url = ''
        make_wine_atter_resoult(parse_resoult, page.url, 'image_url', [(e1, image_url_xpath)])
    else:
        make_wine_atter_resoult(parse_resoult)

    if image_url:
        # -- выделим path
        path = parse.urlparse(image_url).path
        # -- построим url
        image_url = parse.urljoin(page.url, path)
        
    return image_url


async def get_availability_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        availability1_xpath = "//div[contains(@class, 'product-shop wait')] | //div[contains(@class, 'product-shop avail')]"
        availability = await page.locator(availability1_xpath).get_attribute('class')
        availability = availability or ''
    except Error as e1:
        availability = ''
        make_wine_atter_resoult(parse_resoult, page.url, 'availability', [(e1, availability1_xpath)])
    else:
        make_wine_atter_resoult(parse_resoult)

    match availability.split():
        case [_, a]:
            availability = a
        case _:
            pass

    return availability


async def get_name_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        name1_xpath = "xpath=//div[@class='product-translation']/span"
        name = await page.locator(name1_xpath).text_content()
        name = name or ''
    except Error as e1:
        try:
            name2_xpath = "xpath=//div[contains(@class, 'product-title')]/h1"
            name =  await page.locator(name2_xpath).locator("..").text_content()
            name = name or ''
        except Error as e2:
            name = ''
            make_wine_atter_resoult(parse_resoult, page.url, 'name', [(e1, name1_xpath), (e2, name2_xpath)])
        else:
            make_wine_atter_resoult(parse_resoult)
    else:
        make_wine_atter_resoult(parse_resoult)

    name = " ".join(name.split())

    return name


async def get_vintage_handle_result(page: Page, parse_resoult: list[WineAtrrResoult]) -> str:
    try:
        vintage1_xpath = "xpath=//div[contains(@class, 'prod_param_2')]/.//option[@selected]"
        vintage = await page.locator(vintage1_xpath).text_content()
        vintage = vintage or ''
    except Error as e1:
        try:
            vintage2_xpath = "xpath=//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]"
            vintage =  await page.locator(vintage2_xpath).locator("..").text_content()
            vintage = vintage or ''
        except Error as e2:
            vintage = ''
            make_wine_atter_resoult(parse_resoult, page.url, 'vintage', [(e1, vintage1_xpath), (e2, vintage2_xpath)])
        else:
            make_wine_atter_resoult(parse_resoult)
    else:
        make_wine_atter_resoult(parse_resoult)

    match vintage.split():
        case [_, v]:
            vintage = v
        case _:
            pass

    return vintage

def make_wine_atter_resoult(parse_resoult: list[WineAtrrResoult], page_url:str = "", attr_name: str = "", err_xpath_list: list[tuple[Error, str]] | None = None):
    if not err_xpath_list:
        parse_resoult.append(WineAtrrResoult())
    else:
        parse_resoult.append(WineAtrrResoult(
            status=ResultStatus.ERROR.value, 
            page_url=page_url, 
            atrr_name=attr_name, 
            err_type="_".join(("-".join([e.__class__.__name__, e.message, x]) for e, x in err_xpath_list))
            )
            )
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--concurency',
                        help='Count of concurrently opened and parsed wine pages',
                        type=int,
                        default=3)
    parser.add_argument('-l', '--less',
                        help='Headless mode. If -l pointed - ' \
                        'borowser run in headless mode. ' \
                        'Default headless=False' ,
                        action='store_true')
    parser.add_argument('-p', '--prod',
                        help="Prodaction mod. If -p not pointed (i.e. set dev mod)"
                        " - parsed only one catalog page.",
                        action='store_true')
    parser.add_argument('-f', '--feed',
                        help='Feed output file. Default feed.json',
                        type=str,
                        default='feed.json')
    parser.add_argument('-r', '--res',
                        help='Parse resoults output file. Default resoult.json',
                        type=str,
                        default='resoult.json')
    args = parser.parse_args()
    return args.concurency if args.concurency > 0 else 1, args.less, args.prod, args.feed, args.res 
    

if __name__ == '__main__':
    # res = asyncio.run(test_main())
    # with open('parse_res.json', 'w') as f:
    #     f.write(json.dumps(res, indent=2))
    print(args())