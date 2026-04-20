import asyncio
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class MSOScraper:
    def __init__(self):
        self.results = {}

    async def scrape_mso(self, name, url):
        print(f"Starting scrape for: {name} at {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            page = await context.new_page()

            try:
                # 1. Scrape Locations
                locations = await self.extract_locations(page, url)

                # 2. Scrape Leadership
                leadership = await self.extract_leadership(page, url)

                self.results[name] = {
                    "url": url,
                    "locations": locations,
                    "leadership": leadership
                }
            except Exception as e:
                print(f"Error scraping {name}: {e}")
            finally:
                await browser.close()

    async def extract_locations(self, page, base_url):
        # Try to find common location page links
        location_paths = ["/locations", "/our-centers", "/facilities", "/find-a-center"]
        locations_data = []

        for path in location_paths:
            try:
                target_url = base_url.rstrip("/") + path
                await page.goto(target_url, wait_until="networkidle", timeout=30000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                # Broad logic: Look for address-like structures or list items
                # This is a skeleton and needs specialization per MSO
                address_elements = soup.select(".location, .address, [itemprop='address']")
                for el in address_elements:
                    locations_data.append(el.get_text(separator=" ", strip=True))

                if locations_data:
                    break # Found something
            except:
                continue

        return list(set(locations_data))

    async def extract_leadership(self, page, base_url):
        leadership_paths = ["/leadership", "/our-team", "/management", "/executive-team"]
        leadership_data = []

        for path in leadership_paths:
            try:
                target_url = base_url.rstrip("/") + path
                await page.goto(target_url, wait_until="networkidle", timeout=30000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                # Look for name/title pairs
                # Common patterns: h3 for names, p or span for titles nearby
                team_members = soup.select(".team-member, .executive, .leader")
                for member in team_members:
                    name = member.select_one("h3, h4, .name")
                    title = member.select_one(".title, .position, .role")
                    if name:
                        name_text = name.get_text(strip=True)
                        title_text = title.get_text(strip=True) if title else "N/A"
                        leadership_data.append({"name": name_text, "title": title_text})

                if leadership_data:
                    break
            except:
                continue

        return leadership_data

    def save_results(self, filename="mso_scrape_results.json"):
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)
        print(f"Results saved to {filename}")

async def main():
    mso_list = [
        {"name": "GI Alliance", "url": "https://gialliance.com"},
        {"name": "USOSM", "url": "https://www.usosm.com"},
        {"name": "Surgery Partners", "url": "https://surgerypartners.com"}
    ]

    scraper = MSOScraper()
    tasks = [scraper.scrape_mso(mso["name"], mso["url"]) for mso in mso_list]
    await asyncio.gather(*tasks)
    scraper.save_results()

if __name__ == "__main__":
    asyncio.run(main())
