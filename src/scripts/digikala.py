import time
import html
import asyncio
from playwright.async_api import async_playwright, Page
from utils.index import save_file
from utils.index import convert_persian_to_english


url = "https://www.digikala.com/landing-page/?has_selling_stock=1&promotion_types%5B0%5D=promotion&page=342"


async def go_to_next_page(page: Page):
    pagination_container = await page.query_selector(
        "div[class*='product-list_ProductList__banner__']"
    )

    if pagination_container:
        next_button = await pagination_container.query_selector('text="بعدی"')
        if next_button:
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
        'div[class*="product-list_ProductList__pagesContainer__"]'
    )

    if product_container:

        products = await product_container.query_selector_all(
            'div[class*="product-list_ProductList__item__"]'
        )
        count = len(products)
        print(f"Found {count} product...")

        for index, product in enumerate(products):
            info = {
                "id": index + offset,
                "title": None,
                "url": None,
                "rate": None,
                "thumbnail": None,
                "alt": None,
                "final_price": None,
                "price_no_discount": None,
                "discount_percent": None,
            }

            # url
            anchor_container = await product.query_selector(
                "a[class*='styles_VerticalProductCard--hover']"
            )
            if anchor_container:
                info["url"] = await anchor_container.get_attribute("href")

            # title
            title_container = await product.query_selector(
                "h3[class*='styles_VerticalProductCard__productTitle__']"
            )
            if title_container:
                raw_title = await title_container.text_content()
                info["title"] = html.unescape(raw_title)

            # rate
            rate_container = await product.query_selector(
                "p.text-body2-strong.text-neutral-700"
            )
            if rate_container:
                raw_rate = await rate_container.text_content()
                info["rate"] = html.unescape(raw_rate)

            # img
            img_container = await product.query_selector("picture img")
            if img_container:
                info["thumbnail"] = await img_container.get_attribute("src")
                raw_alt = await img_container.get_attribute("alt")
                info["alt"] = html.unescape(raw_alt)
            # discount
            discount_container = await product.query_selector(
                "span[data-testid='price-discount-percent']"
            )
            if discount_container:
                discount = await discount_container.text_content()
                info["discount_percent"] = convert_persian_to_english(discount)
            # price no discount
            price_no_discount_container = await product.query_selector(
                "div[data-testid='price-no-discount']"
            )
            if price_no_discount_container:
                raw_price = await price_no_discount_container.text_content()
                info["price_no_discount"] = convert_persian_to_english(raw_price)
            # price
            price_container = await product.query_selector(
                "span[data-testid='price-final']"
            )
            if price_container:
                raw_price = await price_container.text_content()
                info["final_price"] = convert_persian_to_english(raw_price)

            details.append(info)
    else:
        print("❌ Can not find the product container")
    return {"count": count, "details": details}


async def main():
    # init and launch the browser
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        )
        page_number = 342
        offset = 0

        await page.goto(url)
        time.sleep(10)
        while True:
            print("=============================")
            print(f"Scrapping page {page_number}")
            data = await scrape_page(page, offset)
            offset += data["count"]
            save_file(data, f"digikala/{page_number}")
            print(f"✅ Page {page_number} has been written.")
            page_number += 1

            if not await go_to_next_page(page):
                break

        await browser.close()


asyncio.run(main())
