import requests
import csv
import os
import xml.etree.ElementTree as ET
import time
from datetime import datetime

# Keywords for classification
GPO_KEYWORDS = ["VIZIENT", "PREMIER", "PROVISTA", "HEALTHTRUST", "GREENHEALTH", "GROUP PURCHASING", "PURCHASING SERVICES"]
DISTRIBUTOR_KEYWORDS = ["MCKESSON", "CARDINAL HEALTH", "AMERISOURCEBERGEN", "CENCORA", "MEDLINE", "OWENS & MINOR", "MEDICAL SUPPLIES", "PHARMACEUTICALS", "DISTRIBUTION"]

def normalize_text(text):
    if not text:
        return ""
    return text.strip().upper()

def search_hospital(name):
    print(f"Searching for: {name}")
    try:
        url = f"https://projects.propublica.org/nonprofits/api/v2/search.json?q={name}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('organizations'):
                # Prioritize exact matches if possible, otherwise take the first
                for org in data['organizations']:
                    if org['name'].upper() == name.upper():
                        return org
                return data['organizations'][0]
    except Exception as e:
        print(f"  Error searching for {name}: {e}")
    return None

def get_filings(ein):
    try:
        url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Error getting filings for {ein}: {e}")
    return {}

def extract_contractors_from_xml(xml_url):
    contractors = []
    try:
        print(f"  Attempting XML extraction from: {xml_url}")
        response = requests.get(xml_url, timeout=20)
        if response.status_code != 200:
            return contractors

        root = ET.fromstring(response.content)
        # Search for IndependentContractorGrp
        ic_elements = root.findall(".//{http://www.irs.gov/efile}IndependentContractorGrp")
        if not ic_elements:
            ic_elements = root.findall(".//IndependentContractorGrp")

        for ic in ic_elements:
            name = ""
            name_el = ic.find(".//{http://www.irs.gov/efile}BusinessNameLine1Txt") or \
                      ic.find(".//BusinessNameLine1Txt") or \
                      ic.find(".//{http://www.irs.gov/efile}BusinessNameLine1") or \
                      ic.find(".//BusinessNameLine1")
            if name_el is not None:
                name = name_el.text

            desc = ""
            desc_el = ic.find(".//{http://www.irs.gov/efile}DescriptionOfServicesTxt") or \
                      ic.find(".//DescriptionOfServicesTxt") or \
                      ic.find(".//{http://www.irs.gov/efile}DescriptionServices") or \
                      ic.find(".//DescriptionServices")
            if desc_el is not None:
                desc = desc_el.text

            amount = 0
            amount_el = ic.find(".//{http://www.irs.gov/efile}CompensationAmt") or \
                        ic.find(".//CompensationAmt") or \
                        ic.find(".//{http://www.irs.gov/efile}Amount") or \
                        ic.find(".//Amount")
            if amount_el is not None:
                try:
                    amount = float(amount_el.text)
                except:
                    amount = 0

            if name and amount >= 100000:
                contractors.append({
                    'name': name,
                    'description': desc,
                    'amount': amount
                })

        contractors.sort(key=lambda x: x['amount'], reverse=True)
        return contractors[:5]

    except Exception as e:
        print(f"  Error parsing XML: {e}")
    return contractors

def is_target_contractor(name, description):
    combined = normalize_text(name) + " " + normalize_text(description)
    return any(kw in combined for kw in GPO_KEYWORDS + DISTRIBUTOR_KEYWORDS)

def main():
    hospitals = []
    if os.path.exists('target_hospitals.txt'):
        with open('target_hospitals.txt', 'r') as f:
            hospitals = [line.strip() for line in f if line.strip()]

    os.makedirs('data/raw', exist_ok=True)
    output_file = 'data/raw/hospital_contractors_enriched.csv'
    manual_file = 'data/raw/manual_review_needed.csv'

    enriched_fields = ['hospital_ein', 'contractor_name', 'service_description']
    manual_fields = ['hospital_name', 'ein', 'pdf_url', 'notes']

    with open(output_file, 'w', newline='') as csv_enriched, \
         open(manual_file, 'w', newline='') as csv_manual:

        writer_enriched = csv.DictWriter(csv_enriched, fieldnames=enriched_fields)
        writer_enriched.writeheader()

        writer_manual = csv.DictWriter(csv_manual, fieldnames=manual_fields)
        writer_manual.writeheader()

        success_count = 0
        total_processed = 0

        for hosp_name in hospitals[:50]:
            total_processed += 1
            org_search = search_hospital(hosp_name)

            if not org_search:
                print(f"  Hospital NOT FOUND on ProPublica: {hosp_name}")
                writer_manual.writerow({
                    'hospital_name': hosp_name,
                    'ein': 'NOT_FOUND',
                    'pdf_url': 'N/A',
                    'notes': 'Search failed to find organization'
                })
                continue

            ein = org_search['ein']
            actual_name = org_search['name']

            org_details = get_filings(ein)
            filings = org_details.get('filings_with_data', [])
            filings.sort(key=lambda x: x.get('tax_prd_yr', 0), reverse=True)

            found_xml = False
            best_pdf = None

            # Try to find a filing with XML data first
            for filing in filings:
                if filing.get('xml_url'):
                    contractors = extract_contractors_from_xml(filing['xml_url'])
                    target_contractors = [ic for ic in contractors if is_target_contractor(ic['name'], ic['description'])]
                    if target_contractors:
                        for ic in target_contractors:
                            writer_enriched.writerow({
                                'hospital_ein': ein,
                                'contractor_name': ic['name'],
                                'service_description': ic['description']
                            })
                        found_xml = True
                        success_count += 1
                        print(f"  Successfully extracted {len(target_contractors)} target contractors from XML.")
                        break

                if not best_pdf and filing.get('pdf_url'):
                    best_pdf = filing['pdf_url']

            if not found_xml:
                # Fallback to filings_without_data for PDF if needed
                if not best_pdf:
                    no_data = org_details.get('filings_without_data', [])
                    no_data.sort(key=lambda x: x.get('tax_prd_yr', 0), reverse=True)
                    if no_data and no_data[0].get('pdf_url'):
                        best_pdf = no_data[0]['pdf_url']

                print(f"  XML extraction skipped/failed. Adding {actual_name} to manual review.")
                writer_manual.writerow({
                    'hospital_name': actual_name,
                    'ein': ein,
                    'pdf_url': best_pdf or 'N/A',
                    'notes': 'No automated data extracted'
                })

            time.sleep(1) # Rate limit

    print(f"\nExtraction Task Complete.")
    print(f"Enriched Data: {output_file}")
    print(f"Manual Review Needed: {manual_file}")
    if total_processed > 0:
        print(f"Success Rate: {success_count}/{total_processed} ({(success_count/total_processed)*100:.1f}%)")

if __name__ == "__main__":
    main()
