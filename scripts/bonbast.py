import asyncio
import time
from playwright.async_api import async_playwright, Page
from utils.index import generate_dates, save_file

url = "https://bonbast.com/archive"


async def go_to_date(page: Page, date: str):
    input = await page.query_selector("form.form-inline input[type='text']")

    if input:
        await input.focus()
        await input.fill(date)

        # close datepicker
        await input.press("Enter", delay=100)

        # submit form
        await input.press("Enter", delay=100)
        return

    raise ValueError("❌ Can not find form controllers")


async def scrap_page(page: Page):

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


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        )

        data = {}
        await page.goto(url)
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        time.sleep(5)

        year = start_date.split("-")[0]
        for date in generate_dates(start_date, end_date):
            await go_to_date(page, date)

            try:
                await page.wait_for_selector(
                    f"em.miladi:has-text('{date} .')", timeout=3000
                )
            except:
                print(f"Skipped {date} because of error(s)")
            else:
                data[date] = await scrap_page(page)
            finally:
                # preventing the script from sending requests too quickly in succession
                # this allows other tasks to run in the meantime without blocking the event loop.
                await asyncio.sleep(5)
        save_file(data, f"bonbast/{year}")
        await browser.close()


asyncio.run(main())
