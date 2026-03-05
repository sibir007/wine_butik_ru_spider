# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html



from decimal import Decimal, localcontext
from itemloaders.processors import MapCompose
from scrapy import Item, Field
from dataclasses import dataclass, field
from functools import partial


def str_mum_san(value: str) -> str:
    return value.strip().replace(' ', '').replace(',', '')

def float_checker(pres: int, value: str | None) -> float | None:
    if value is None:
        return value
    try:
        res = round(float(str_mum_san(value)), pres)
    except:
        res = None
    return res

def int_checker(value: str | None) -> int | None:
    if value is None:
        return value
    try:
        res = int(str_mum_san(value))
    except:
        res = None
    return res

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

