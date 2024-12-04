import time
import os
import json
import asyncio
from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async


base_url = "https://www.amazon.com"


def absolute_url(page: Page, relative_url: str):
    if relative_url == None:
        return None
    return page.url + relative_url


async def go_to_next_page(page: Page):
    pagination_container = await page.query_selector("span.s-pagination-strip ul")

    if pagination_container:
        next_button = await pagination_container.query_selector('text="Next"')

        if next_button:
            is_disable = await next_button.get_attribute("aria-disabled") == "true"

            if is_disable:
                print("ℹ️ Next button is disable, terminating the process")
                return False

            await next_button.click()
            time.sleep(3)
            return True
        else:
            print("❌ Can not find next button")
    else:
        print("❌ Can not find pagination")
    return False


async def scrape_page(page: Page, offset: int):
    details = []
    count = 0
    product_container = await page.query_selector(
        'span[data-component-type="s-search-results"]'
    )

    if product_container:

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
                    info["rate"] = await first_span.get_attribute("aria-label")

                if second_span:
                    info["rate_count"] = await second_span.inner_text()
            # image
            if image_container:
                img = await image_container.query_selector("img")

                if img:
                    info["alt"] = await img.get_attribute("alt")
                    info["thumbnail"] = await img.get_attribute("src")

            # price
            if price_container:
                prices = await price_container.query_selector_all("span.a-offscreen")
                info["price"] = [await price.text_content() for price in prices]

            details.append(info)
    else:
        print("Can not find the product container")
    return {"count": count, "details": details}


def save_file(data, path: str):
    # ensure the directory exists
    directory = os.path.dirname(f"data/amazon/{path}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # pick last segment as file name
    segment = path.split("/")

    # write the data to a JSON file
    with open(f"{directory}/{segment[-1]}.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def convert_to_plus_format(text: str):
    return text.strip().replace(" ", "+")


async def main():
    # init and launch the browser
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
        )
        page_number = 1
        offset = 0
        query = input("Enter the query and press 'ENTER':\n")
        formattedQuery = convert_to_plus_format(query)

        # apply stealth techniques
        await stealth_async(page)
        await page.goto(base_url + f"/s?k={formattedQuery}")

        while True:
            print("=============================")
            print(f"Scrapping page {page_number}")
            data = await scrape_page(page, offset)
            offset += data["count"]
            save_file(data, f"{query}/{page_number}")
            print(f"✅ Page {page_number} has been written.")
            page_number += 1

            if not await go_to_next_page(page):
                break

        await browser.close()


asyncio.run(main())
