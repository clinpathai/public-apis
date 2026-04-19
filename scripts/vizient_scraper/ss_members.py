import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re

def scrape_ss_members():
    url = "https://www.vizientsouthernstates.com/members"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    access_date = datetime.now().strftime("%Y-%m-%d")

    # Heuristic: exclude known navigation or footer keywords
    exclude_keywords = {'PRIVACY POLICY', 'TERMS OF USE', 'CAREERS', 'EVENTS', 'NEWSROOM', 'CONTACT US', 'ABOUT US', 'HOME', 'OUR SOLUTIONS', 'MEMBERSHIP', 'PHOENIX COMPANIES', 'VIZIENT INC'}

    headers = soup.find_all(re.compile('^h[1-6]$'))

    section_map = []
    for h in headers:
        text = h.get_text(strip=True).upper()
        if 'STOCKHOLDERS' in text:
            section_map.append((h, 'confirmed_member'))
        elif 'REGIONAL AFFILIATE' in text:
            section_map.append((h, 'regional_affiliate_member'))
        elif 'NETWORK AFFILIATES' in text:
            section_map.append((h, 'member_network_participant'))

    if not section_map:
        headers = soup.find_all(['strong', 'b'])
        for h in headers:
            text = h.get_text(strip=True).upper()
            if 'STOCKHOLDERS' in text:
                section_map.append((h, 'confirmed_member'))
            elif 'REGIONAL AFFILIATE' in text:
                section_map.append((h, 'regional_affiliate_member'))
            elif 'NETWORK AFFILIATES' in text:
                section_map.append((h, 'member_network_participant'))

    for i, (header, rel_type) in enumerate(section_map):
        next_header = section_map[i+1][0] if i+1 < len(section_map) else None

        curr = header.find_next()
        while curr and curr != next_header:
            if curr.name == 'a' and curr.get('href') and not curr.get('href').startswith('#'):
                text = curr.get_text(strip=True)
                if text and len(text) > 3 and text.upper() not in exclude_keywords:
                    # Additional check for generic titles in porto theme
                    if text in ['About Us', 'Newsroom', 'Events', 'Careers', 'Contact Us', 'Home', 'Our Solutions', 'Membership', 'Phoenix Companies', 'Vizient Inc', 'Privacy Policy', 'Terms of Use']:
                        curr = curr.find_next()
                        continue

                    match = re.search(r'([A-Z][a-z\s\.]+),\s*([A-Z]{2})$', text)
                    city = ""
                    state = ""
                    org_name = text
                    if match:
                        city = match.group(1).strip()
                        state = match.group(2).strip()
                        org_name = text[:match.start()].strip().rstrip(' +*')

                    if not city and ',' in text:
                        parts = text.split(',')
                        if len(parts) >= 2:
                            maybe_state = parts[-1].strip()
                            if len(maybe_state) == 2 and maybe_state.isupper():
                                state = maybe_state
                                city = parts[-2].strip()
                                org_name = ",".join(parts[:-2]).strip().rstrip(' +*')

                    confidence = 1.0 if rel_type == 'confirmed_member' else 0.8
                    is_confirmed = True if rel_type == 'confirmed_member' else False

                    data.append({
                        "source_name": "Vizient Southern States Members Page",
                        "source_url": url,
                        "source_publish_date": None,
                        "source_access_date": access_date,
                        "organization_name_raw": text,
                        "normalized_organization_name": org_name,
                        "organization_type": "hospital",
                        "city": city,
                        "state": state,
                        "relationship_type": rel_type,
                        "relationship_description": f"Listed under {rel_type.replace('_', ' ')}",
                        "evidence_text_short": f"Listed on Vizient SS members page: {text}",
                        "confidence_score": confidence,
                        "gpo_name": "Vizient",
                        "gpo_confidence": confidence,
                        "is_confirmed_gpo_member": is_confirmed,
                        "notes": "",
                        "extraction_method": "html",
                        "created_at": datetime.now().isoformat()
                    })
            curr = curr.find_next()

    df = pd.DataFrame(data).drop_duplicates(subset=['organization_name_raw', 'city', 'state'])
    os.makedirs("data/raw/vizient_public_sources/", exist_ok=True)
    df.to_csv("data/raw/vizient_public_sources/ss_members_raw.csv", index=False)
    print(f"Scraped {len(df)} members from Vizient Southern States")

if __name__ == "__main__":
    scrape_ss_members()
