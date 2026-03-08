from collections.abc import Coroutine

from playwright.async_api import async_playwright, Page, expect
from scrapy import Selector
from scrapy.http import HtmlResponse, Response
from scrapy import Request

# from wine_butik_ru_spider.items import Wine, Prise
import logging
import asyncio

# page = 'https://playwright.dev/'
page = 'https://wine-butik.ru/'
# page = 'https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html'


async def get_page_title(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            # channel='chrome',
            headless=False,
            args=["--start-maximized", '--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()
        # browser = await p.firefox.launch()
        # page = await browser.new_page()
        await page.goto(url)
        await page.locator("//span[contains(@class, 'button')]").click()
        await page.locator("//button[contains(text(), 'Я согласен')]").click()
        
        wine_link = page.locator('#cat_330')
        # print(wine_link)
        await wine_link.hover()
        # print(wine_link)
        await wine_link.click()
        # print(wine_link)
        count_page_selector = page.locator("//select[@name='page']")
        # await count_page_selector.click()
        # p_40 = count_page_selector.locator('//option[@value="40"]')
        # await expect(p_40).to_be_visible()
        # await p_40.hover()

        # await p_40.click()

        

        await page.wait_for_timeout(200000)
        # pt = await page.title()
        
        await browser.close()
    return True

