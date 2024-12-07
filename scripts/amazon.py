import time
import asyncio
import re

from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async
from utils.index import save_file
from utils.index import absolute_url


async def go_to_next_page(page: Page):
    await page.wait_for_selector(
        "span.s-pagination-strip ul",
        timeout=5000,
    )
    pagination_container = await page.query_selector("span.s-pagination-strip ul")

    if pagination_container:
        next_button = await pagination_container.query_selector('text="Next"')

        if next_button:
            is_disable = await next_button.get_attribute("aria-disabled") == "true"

            if is_disable:
                print("ℹ️ Next button is disable, terminating the process")
                return False

            await next_button.click()
            await page.wait_for_selector(
                "h2.a-size-medium-plus.a-spacing-none.a-color-base.a-text-bold:has-text('Results')",
                timeout=5000,
            )
            # await asyncio.sleep(3)
            return True
        else:
            print("❌ Can not find next button")
    else:
        print("❌ Can not find pagination")
    return False


async def scrape_page(page: Page, offset: int):
    details = []
    count = 0
    await page.wait_for_selector(
        'span[data-component-type="s-search-results"]', timeout=3000
    )
    product_container = await page.query_selector(
        'span[data-component-type="s-search-results"]'
    )

    if product_container:
        await page.wait_for_function(
            "document.querySelectorAll('div[data-component-type=\"s-search-result\"]').length > 20",
            timeout=3000,
        )
        products = await product_container.query_selector_all(
            'div[data-component-type="s-search-result"]'
        )
        count = len(products)
        print(f"Found {count} product...")

        for index, product in enumerate(products):
            info = {
                "id": index + offset,
                "uuid": None,
                "title": None,
                "url": None,
                "rate": None,
                "rate_count": None,
                "thumbnail": None,
                "alt": None,
                "price": [],
            }
            info["uuid"] = await product.get_attribute("data-uuid")
            title_container = await product.query_selector(
                "div[data-cy='title-recipe']"
            )
            review_container = await product.query_selector(
                "div[data-cy='reviews-block']"
            )
            price_container = await product.query_selector(
                "div[data-cy='price-recipe']"
            )
            image_container = await product.query_selector(
                "span[data-component-type='s-product-image']"
            )

            # url
            if title_container:
                title_url = await title_container.query_selector("a")
                info["title"] = await title_container.text_content()

                if title_url:
                    info["url"] = absolute_url(
                        page, await title_url.get_attribute("href")
                    )

            # rating
            if review_container:
                first_span = await review_container.query_selector(
                    "div:first-child > span"
                )
                second_span = await review_container.query_selector(
                    "div:first-child > span:nth-of-type(2)"
                )

                if first_span:
                    raw_rate = await first_span.get_attribute("aria-label")
                    if raw_rate:
                        rate_match = re.search(r"(\d+(\.\d+)?)", raw_rate)
                        info["rate"] = rate_match

                if second_span:
                    raw_rate_count = await second_span.inner_text()
                    info["rate_count"] = int(raw_rate_count.replace(",", ""))
            # image
            if image_container:
                img = await image_container.query_selector("img")

                if img:
                    info["alt"] = await img.get_attribute("alt")
                    info["thumbnail"] = await img.get_attribute("src")

            # price
            if price_container:
                prices = await price_container.query_selector_all("span.a-offscreen")
                for price in prices:
                    raw_txt = await price.text_content()

                    if raw_txt:
                        price = float(raw_txt.replace("$", "").replace(",", ""))
                        info["price"].append(price)

            details.append(info)
    else:
        print("❌ Can not find the product container")
    return {"count": count, "details": details}


def convert_to_plus_format(text: str):
    return text.strip().replace(" ", "+")


async def main():
    page_number = 1
    base_url = f"https://www.amazon.com/s?i=baby-products-intl-ship&srs=16225005011&rh=n%3A16225005011&s=popularity-rank&fs=true&ref=lp_16225005011_sar&page=1"
    # init and launch the browser
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
        )
        offset = 0

        # apply stealth techniques
        await stealth_async(page)
        await page.goto(base_url)

        while True:
            print("=============================")
            print(f"Scrapping page {page_number}")
            data = await scrape_page(page, offset)
            offset += data["count"]
            save_file(data, f"amazon/baby/{page_number}")
            print(f"✅ Page {page_number} has been written.")
            page_number += 1

            if not await go_to_next_page(page):
                break

        await browser.close()


asyncio.run(main())
