from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

async def get_dataset_gz_links(hub_url):
    dataset_gz_links = []

    real_base = "https://xenabrowser.net/datapages/"  # for href resolution

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Visit initial hub URL
        await page.goto(hub_url, wait_until="networkidle")
        await page.wait_for_selector("a[href*='?cohort=']", timeout=15000)

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Step 2: Extract cohort links using real base
        cohort_links = [
            urllib.parse.urljoin(real_base, a["href"])
            for a in soup.select("a[href*='?cohort=']")
        ]

        for cohort_url in cohort_links:
            print(cohort_url)
            cohort_page = await context.new_page()
            await cohort_page.goto(cohort_url, wait_until="networkidle")
            await cohort_page.wait_for_timeout(2000)

            html = await cohort_page.content()
            soup = BeautifulSoup(html, "html.parser")

            target_element = soup.find("a", string="IlluminaHiSeq pancan normalized")
            if not target_element:
                await cohort_page.close()
                continue

            dataset_href = urllib.parse.urljoin(real_base, target_element["href"])
            print(dataset_href)
            await cohort_page.goto(dataset_href, wait_until="networkidle")
            await cohort_page.wait_for_timeout(2000)

            html = await cohort_page.content()
            soup = BeautifulSoup(html, "html.parser")

            gz_link_tag = soup.find("a", href=lambda href: href and href.endswith(".gz"))
            if gz_link_tag:
                dataset_gz_links.append(gz_link_tag["href"])

            await cohort_page.close()

        await browser.close()

    return dataset_gz_links
