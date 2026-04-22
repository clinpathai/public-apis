import asyncio
import pandas as pd
import os
import sys
from playwright.async_api import async_playwright

async def scrape_340b_opais(target_ids=None, limit=10):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        results = []

        try:
            print("Navigating to HRSA 340B OPAIS home page...")
            await page.goto("https://340bopais.hrsa.gov/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            print("Accessing Covered Entity Search...")
            search_button = page.locator("div.hs-big-button", has_text="Search Covered Entities").locator("button")
            await search_button.click()
            await page.wait_for_selector("input[placeholder='Enter the text to search']", timeout=30000)

            if not target_ids:
                print("No targets provided. Filtering for DSH...")
                combo = page.locator("dxbl-combo-box").first
                await combo.click()
                await asyncio.sleep(2)
                dsh_item = page.locator(".dxbl-list-item", has_text="DSH")
                if await dsh_item.count() > 0:
                    await dsh_item.first.click()
                    await page.locator("button.dxbl-btn-primary", has_text="Search").click()
                    await asyncio.sleep(5)

                links = page.locator("a[title='View 340B Details']")
                count = await links.count()
                limit = min(limit, count)
                ids_to_process = []
                for i in range(limit):
                    ids_to_process.append(await links.nth(i).inner_text())
            else:
                ids_to_process = target_ids

            for tid in ids_to_process:
                print(f"--- Processing Hospital ID: {tid} ---")
                await page.fill("input[placeholder='Enter the text to search']", tid)
                await page.locator("button.dxbl-btn-primary", has_text="Search").click()
                await asyncio.sleep(5)

                link = page.locator("a", has_text=tid).first
                if not await link.is_visible():
                    print(f"Hospital {tid} not found in search results.")
                    continue

                await link.click()
                await page.wait_for_selector(".alert-success", timeout=30000)
                await asyncio.sleep(2)

                banner_text = await page.locator(".alert-success").first.inner_text()
                hospital_name = banner_text.split(" ", 1)[1].split("\n")[0].replace("(Active)", "").strip()

                ccn = ""
                ccn_label = page.locator("div.col-6", has_text="Medicare Provider Number")
                if await ccn_label.count() > 0:
                    ccn = await page.locator("div.col-6:has-text('Medicare Provider Number') + div").inner_text()

                print(f"Scraping pharmacies for: {hospital_name} (CCN: {ccn})")

                pharmacy_tab = page.locator("dxbl-tab-item", has_text="Contract Pharmacies")
                if await pharmacy_tab.count() > 0:
                    await pharmacy_tab.click()
                    await asyncio.sleep(5)

                    has_next = True
                    page_num = 1
                    while has_next:
                        rows = page.locator("tr[data-visible-index]")
                        row_count = await rows.count()
                        print(f"Found {row_count} pharmacies on page {page_num}.")

                        for j in range(row_count):
                            cells = rows.nth(j).locator("td")
                            # Based on HTML observation:
                            # 1: Pharmacy Name (link)
                            # 2: Address (sometimes DBA)
                            # 3: Address or City
                            # This structure is complex. We will use a more robust way to find status.

                            row_text = await rows.nth(j).inner_text()
                            # We want "Active" pharmacies.
                            # Usually, Terminated pharmacies have a termination date in one of the columns.
                            # In the DSH210009 sample, status wasn't explicit in a 'Status' column but dates were.

                            # Let's try to extract fields by index cautiously
                            texts = [await cells.nth(k).inner_text() for k in range(await cells.count())]

                            # Heuristic for DSH hospitals:
                            # 0: Contract Detail
                            # 1: Pharmacy Name
                            # 2: Address/DBA
                            # 3: Address
                            # ...
                            # 11: Term Date (if exists)

                            p_name = texts[1] if len(texts) > 1 else ""
                            p_address = ", ".join([t.strip() for t in texts[2:7] if t.strip() and t != "&nbsp;"])

                            # Term date is usually near the end. Index 11 in Johns Hopkins sample.
                            term_date = texts[11] if len(texts) > 11 else ""

                            if not term_date.strip() or term_date.strip() == "&nbsp;":
                                results.append({
                                    "hospital_340b_id": tid,
                                    "hospital_name": hospital_name,
                                    "ccn": ccn.strip(),
                                    "contract_pharmacy_name": p_name.strip(),
                                    "pharmacy_address": p_address,
                                    "status": "Active",
                                    "effective_date": texts[8] if len(texts) > 8 else ""
                                })

                        next_btn = page.locator("button[aria-label='Next page']").first
                        if await next_btn.is_visible() and await next_btn.is_enabled():
                            await next_btn.click()
                            await asyncio.sleep(5)
                            page_num += 1
                        else:
                            has_next = False
                else:
                    print(f"No Contract Pharmacies tab found for {tid}")

                await page.goto("https://340bopais.hrsa.gov/SearchCoveredEntities")
                await page.wait_for_selector("input[placeholder='Enter the text to search']", timeout=30000)
                clear_btn = page.locator("button", has_text="Clear").first
                if await clear_btn.is_enabled():
                    await clear_btn.click()
                await asyncio.sleep(2)

        except Exception as e:
            print(f"Error during scraping: {e}")

        finally:
            await browser.close()

        return results

if __name__ == "__main__":
    targets = ["DSH440039", "DSH210009", "DSH460009"]
    data = asyncio.run(scrape_340b_opais(target_ids=targets))

    if not data:
        df = pd.DataFrame(columns=["hospital_340b_id", "hospital_name", "ccn", "contract_pharmacy_name", "pharmacy_address", "status", "effective_date"])
    else:
        df = pd.DataFrame(data)

    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/opais_raw_extract.csv", index=False)
    print(f"Scraped {len(data)} total records. Saved to data/raw/opais_raw_extract.csv")
