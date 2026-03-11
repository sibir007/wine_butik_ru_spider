import logging
from urllib import parse


WINE_CARDS_XPATH: str = "//div[@class='catalog-item']"
WINE_HREFS_XPATH: str = ".//div[@class='catalog-item__desc']/h2/a[@href]/@href"
NEXT_PAGE_XPATH: str = "//div[@class='paging_box']/.//a[@class='next']/@value"
WINE_NAME1_XPATH: str = "//div[contains(@class, 'product-translation')]/span/text()[normalize-space()]"
WINE_NAME2_XPATH: str = "//div[contains(@class, 'product-title')]/h1/text()[normalize-space()]"
VINTAGE1_XPATH: str = "//div[contains(@class, 'prod_param_2')]/.//option[@selected]/text()"
VINTAGE2_XPATH: str = "//div[contains(@class, 'prod_param_2')]/p/em[contains(text(), 'Год')]/../text()"
AVAILABILITY_XPATH: str = "//div[contains(@class, 'product-shop wait')]/@class | //div[contains(@class, 'product-shop avail')]/@class"
IMG_URL_XPATH: str = "//img[contains(@class, 'product-image-large')]/@src"
PRICE_XPATH: str = "//div[contains(@id, 'product-price')]/div[2]/text()"
CURRENCY_XPATH: str = "//div[contains(@id, 'product-price')]/div[3]/text()"
VOLUME1_XPATH: str = "//div[@class='product-params']/p/em[contains(text(), 'Объем')]/../text()"
VOLUME2_XPATH: str = "//div[@class='product-params']/p/em[contains(text(), 'Объем')]/..//option[@selected]/text()"



def availability_convert(availability: str) -> str:
    # -- выдаётся в форме 'product-shop wait' или 'product-shop avail'
    match availability.split():
        case [_, a]:
            availability = a
        case _:
            logging.log(msg=f'unrecognized value of availability: {availability}', level=logging.ERROR)
            availability = ''
    return availability


def image_url_conver(base_url, image_url) -> str:
    if image_url:
        # -- выделим path
        # image_url = response.urljoin(image_url)
        path = parse.urlparse(image_url).path
        # -- построим url
        image_url = parse.urljoin(base_url, path)
    return image_url

def volume_convert(volume) -> str:
    match volume.split():
        case [v, _]:
            try:
                volume = str(int(float(v)*1000)) + 'ml'
            except ValueError as e:
                logging.log(msg=e, level=logging.ERROR)
                volume = ''
        case _:
            logging.log(msg=f'unrecognized value of volume: {volume}', level=logging.ERROR)
            volume = ''
    return volume
