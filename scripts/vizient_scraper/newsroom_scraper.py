import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re

def scrape_newsroom():
    url = "https://www.vizientinc.com/newsroom/news-releases"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    access_date = datetime.now().strftime("%Y-%m-%d")

    # Based on the text output, news release links are found in the list
    releases = soup.find_all('a', href=re.compile(r'/newsroom/news-releases/'))

    seen_urls = set()

    for release in releases:
        title = release.get_text(strip=True)
        if not title or len(title) < 10: continue

        release_url = "https://www.vizientinc.com" + release.get('href') if release.get('href').startswith('/') else release.get('href')
        if release_url in seen_urls: continue
        seen_urls.add(release_url)

        # Heuristic extraction from titles
        # Patterns for confirmed relationships in titles

        # "Vizient and [Org] expand agreement"
        match_expand = re.search(r'Vizient and (.*?) expand agreement', title)
        # "[Org] and Vizient announce..."
        match_announce = re.search(r'(.*?) and Vizient announce', title)
        # "Vizient partnership helps [Org]..."
        match_partnership = re.search(r'Vizient partnership helps (.*?) reach', title)

        found_orgs = []
        rel_type = "public_vizient_relationship_signal"
        description = title
        confidence = 0.8
        is_confirmed = False

        if match_expand:
            found_orgs.append(match_expand.group(1))
            rel_type = "new_or_renewed_customer"
            is_confirmed = True
        elif match_announce:
            found_orgs.append(match_announce.group(1))
            rel_type = "new_or_renewed_customer"
            is_confirmed = True
        elif match_partnership:
            found_orgs.append(match_partnership.group(1))
            rel_type = "member_network_participant"
            is_confirmed = True

        for org in found_orgs:
            data.append({
                "source_name": "Vizient Newsroom",
                "source_url": release_url,
                "source_publish_date": None, # Could extract from subpage
                "source_access_date": access_date,
                "organization_name_raw": org,
                "normalized_organization_name": org,
                "organization_type": "unknown",
                "city": "",
                "state": "",
                "relationship_type": rel_type,
                "relationship_description": description,
                "evidence_text_short": f"News Release: {title}",
                "confidence_score": confidence,
                "gpo_name": "Vizient",
                "gpo_confidence": 1.0,
                "is_confirmed_gpo_member": is_confirmed,
                "notes": f"Detected from news release title",
                "extraction_method": "html",
                "created_at": datetime.now().isoformat()
            })

        # Special case: "new and renewed clients"
        if "new and renewed clients" in title.lower():
            try:
                sub_resp = requests.get(release_url, timeout=30)
                sub_soup = BeautifulSoup(sub_resp.content, 'html.parser')
                # Based on view_text_website, they are in a list
                # Look for "The new and renewed client agreements include:"
                body_text = sub_soup.get_text()
                if "new and renewed client agreements include" in body_text:
                    # Find the <ul> following the paragraph
                    target_p = sub_soup.find(lambda tag: tag.name == 'p' and "new and renewed client agreements include" in tag.text)
                    if target_p:
                        ul = target_p.find_next('ul')
                        if ul:
                            items = ul.find_all('li')
                            for item in items:
                                org_name = item.get_text(strip=True)
                                if org_name:
                                    data.append({
                                        "source_name": "Vizient Newsroom Detail",
                                        "source_url": release_url,
                                        "source_publish_date": None,
                                        "source_access_date": access_date,
                                        "organization_name_raw": org_name,
                                        "normalized_organization_name": org_name,
                                        "organization_type": "unknown",
                                        "city": "",
                                        "state": "",
                                        "relationship_type": "new_or_renewed_customer",
                                        "relationship_description": f"Listed in news release: {title}",
                                        "evidence_text_short": f"Listed as new or renewed client in official news release",
                                        "confidence_score": 1.0,
                                        "gpo_name": "Vizient",
                                        "gpo_confidence": 1.0,
                                        "is_confirmed_gpo_member": True,
                                        "notes": "Extracted from news release client list",
                                        "extraction_method": "html",
                                        "created_at": datetime.now().isoformat()
                                    })
            except Exception as e:
                print(f"Error scraping subpage {release_url}: {e}")

    df = pd.DataFrame(data).drop_duplicates(subset=['organization_name_raw', 'source_url'])
    os.makedirs("data/raw/vizient_public_sources/", exist_ok=True)
    df.to_csv("data/raw/vizient_public_sources/newsroom_raw.csv", index=False)
    print(f"Scraped {len(df)} signals from Vizient Newsroom")

if __name__ == "__main__":
    scrape_newsroom()
