import asyncio
import time
from playwright.async_api import async_playwright, Page
from utils.index import generate_dates, save_file

url = "https://bonbast.com/archive"


async def scrap_page(page: Page, date: str):
    date_picker = await page.query_selector("form.form-inline input[type='text']")
    form = await page.query_selector("form.form-inline")

    if date_picker and form:
        await page.fill("form.form-inline input[type='text']", date, timeout=2000)
        await page.locator("form.form-inline").click()
        time.sleep(3)
        tables = await page.query_selector_all("table")

        if tables:
            info = {}
            for index, table in enumerate(tables):

                # currency table
                if index < 2:
                    rows = await table.query_selector_all("tr:not(.info)")

                    if rows:
                        for index, row in enumerate(rows):
                            tds = await row.query_selector_all("td")

                            # [0] --> Code
                            # [1] --> Currency
                            # [2] --> Sell (this number is important)
                            # [3] --> Buy
                            if tds:
                                code = await tds[0].text_content()
                                sell = await tds[2].text_content()
                                # only pick the valid prices
                                if (
                                    sell != None
                                    and code != None
                                    and sell not in ["", "None", "0"]
                                ):
                                    info[code] = sell
                # coin table
                elif index == 2:
                    rows = await table.query_selector_all("tr:not(.info)")

                    if rows:
                        for index, row in enumerate(rows):
                            tds = await row.query_selector_all("td")

                            # [0] --> Coin
                            # [1] --> Sell (this number is important)
                            # [2] --> Buy
                            if tds:
                                code = await tds[0].text_content()
                                sell = await tds[1].text_content()
                                # only pick the valid prices
                                if (
                                    sell != None
                                    and code != None
                                    and sell not in ["", "None", "0"]
                                ):
                                    info[code] = sell
            return info
    else:
        print("❌ Can not find form controllers")


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        )

        data = {}
        await page.goto(url)
        start_date = "2024-10-20"
        end_date = "2024-11-20"
        time.sleep(5)

        year = start_date.split("-")[0]
        for date in generate_dates(start_date, end_date):
            data[date] = await scrap_page(page, date)
        save_file(data, f"bonbast/{year}")
        await browser.close()


asyncio.run(main())
