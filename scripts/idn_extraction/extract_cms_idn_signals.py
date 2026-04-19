import requests
import pandas as pd
import datetime
import os
import time

def fetch_cms_data(dataset_id, limit=1000):
    results = []
    offset = 0
    while True:
        url = f"https://data.cms.gov/provider-data/api/1/datastore/query/{dataset_id}/0?limit={limit}&offset={offset}"
        print(f"Fetching {url}...")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('results', [])
            if not data:
                break
            results.extend(data)
            offset += limit
            if offset >= 10000:
                break
            time.sleep(0.5)
        else:
            print(f"Error fetching data: {response.status_code}")
            break
    return results

def normalize_name(name):
    if not name:
        return ""
    return name.strip().upper()

def identify_idn(facility_name):
    if not facility_name:
        return None, None, None, 0.0
    facility_name_upper = facility_name.upper()

    # Comprehensive mappings
    idn_mappings = {
        "ASCENSION": "Ascension",
        "HCA ": "HCA Healthcare",
        "TENET ": "Tenet Healthcare",
        "KAISER ": "Kaiser Permanente",
        "PROVIDENCE ": "Providence",
        "TRINITY HEALTH": "Trinity Health",
        "COMMONSPIRIT": "CommonSpirit Health",
        "ADVENTHEALTH": "AdventHealth",
        "ATRIUM HEALTH": "Atrium Health",
        "BAYLOR SCOTT & WHITE": "Baylor Scott & White Health",
        "CLEVELAND CLINIC": "Cleveland Clinic",
        "MAYO CLINIC": "Mayo Clinic",
        "NORTHWELL HEALTH": "Northwell Health",
        "UPMC": "UPMC",
        "BANNER HEALTH": "Banner Health",
        "INTERMOUNTAIN": "Intermountain Healthcare",
        "SUTTER HEALTH": "Sutter Health",
        "GEISINGER": "Geisinger",
        "OCHSNER": "Ochsner Health",
        "SANFORD HEALTH": "Sanford Health",
        "NOVANT HEALTH": "Novant Health",
        "MERCY ": "Mercy",
        "BAPTIST HEALTH": "Baptist Health",
        "METHODIST ": "Methodist Health System",
        "ST. LUKE'S": "St. Luke's Health System",
        "AULTMAN": "Aultman Health Foundation",
        "HACKENSACK MERIDIAN": "Hackensack Meridian Health",
        "PRESBYTERIAN ": "Presbyterian Healthcare Services",
        "BON SECOURS": "Bon Secours Mercy Health",
        "MEDSTAR HEALTH": "MedStar Health",
        "JOHNS HOPKINS": "Johns Hopkins Medicine",
        "JEFFERSON HEALTH": "Jefferson Health",
        "MAIN LINE HEALTH": "Main Line Health",
        "PENN MEDICINE": "Penn Medicine",
        "SENTARA": "Sentara Healthcare",
        "LIFEPOINT": "LifePoint Health",
        "SCRIPPS": "Scripps Health",
        "SHARP HEALTHCARE": "Sharp HealthCare",
        "MEMORIAL HERMANN": "Memorial Hermann Health System",
        "METHODIST LE BONHEUR": "Methodist Le Bonheur Healthcare",
        "PRISMA HEALTH": "Prisma Health",
        "BAYLOR COLLEGE OF MEDICINE": "Baylor College of Medicine",
        "BETH ISRAEL LAHEY": "Beth Israel Lahey Health",
        "CEDARS-SINAI": "Cedars-Sinai",
        "CHRISTUS HEALTH": "CHRISTUS Health",
        "DUKE HEALTH": "Duke Health",
        "EMORY HEALTHCARE": "Emory Healthcare",
        "FROEDTERT": "Froedtert Health",
        "HENRY FORD": "Henry Ford Health System",
        "IU HEALTH": "Indiana University Health",
        "LOMA LINDA": "Loma Linda University Health",
        "LOYOLA MEDICINE": "Loyola Medicine",
        "MASS GENERAL BRIGHAM": "Mass General Brigham",
        "MASSACHUSETTS GENERAL": "Mass General Brigham",
        "BRIGHAM AND WOMEN'S": "Mass General Brigham",
        "MONTEFIORE": "Montefiore Health System",
        "MOUNT SINAI": "Mount Sinai Health System",
        "NYU LANGONE": "NYU Langone Health",
        "OHSU": "OHSU Health",
        "ORLANDO HEALTH": "Orlando Health",
        "RUSH UNIVERSITY": "Rush University System for Health",
        "STANFORD HEALTH": "Stanford Health Care",
        "TEMPLE HEALTH": "Temple Health",
        "THOMAS JEFFERSON UNIVERSITY": "Jefferson Health",
        "UC HEALTH": "UC Health",
        "UCLA HEALTH": "UCLA Health",
        "UCSD HEALTH": "UC San Diego Health",
        "UCSF HEALTH": "UCSF Health",
        "UF HEALTH": "UF Health",
        "UMASS MEMORIAL": "UMass Memorial Health",
        "UNC HEALTH": "UNC Health",
        "UNIVERSITY OF CHICAGO": "UChicago Medicine",
        "UNIVERSITY OF IOWA": "UI Health Care",
        "UNIVERSITY OF MIAMI": "UHealth",
        "UNIVERSITY OF MICHIGAN": "Michigan Medicine",
        "UNIVERSITY OF PENNSYLVANIA": "Penn Medicine",
        "UNIVERSITY OF PITTSBURGH": "UPMC",
        "UNIVERSITY OF ROCHESTER": "UR Medicine",
        "UNIVERSITY OF VIRGINIA": "UVA Health",
        "UNIVERSITY OF WASHINGTON": "UW Medicine",
        "UT HEALTH": "UT Health",
        "VANDERBILT": "Vanderbilt University Medical Center",
        "VIRGINIA COMMONWEALTH": "VCU Health",
        "WAKE FOREST": "Atrium Health Wake Forest Baptist",
        "WELLSTAR": "Wellstar Health System",
        "YALE NEW HAVEN": "Yale New Haven Health",
        "ENCOMPASS HEALTH": "Encompass Health",
        "SCIONHEALTH": "ScionHealth",
        "KINDRED ": "Kindred Healthcare",
        "SELECT MEDICAL": "Select Medical",
    }

    for key, value in idn_mappings.items():
        if key in facility_name_upper:
            return value, "inferred_idn_relationship", f"Facility name contains '{key}'", 0.8

    return None, None, None, 0.0

def main():
    access_date = datetime.date.today().isoformat()
    signals = []

    datasets = [
        {"id": "xubh-q36u", "name": "CMS Hospital General Information", "fn_col": "facility_name", "type": "hospital"},
        {"id": "7t8x-u3ir", "name": "CMS Inpatient Rehabilitation Facility - General Information", "fn_col": "provider_name", "type": "IRF"},
        {"id": "azum-44iv", "name": "CMS Long-Term Care Hospital - General Information", "fn_col": "provider_name", "type": "LTCH"},
        {"id": "6jpm-sxkc", "name": "CMS Home Health Care Agencies", "fn_col": "agency_name", "type": "HHA"},
    ]

    for ds in datasets:
        print(f"Fetching {ds['name']}...")
        data = fetch_cms_data(ds['id'], limit=1000)
        for entry in data:
            facility_name = entry.get(ds['fn_col'], '')
            city = entry.get('citytown', entry.get('city', ''))
            state = entry.get('state', '')

            idn_name, rel_type, rel_desc, confidence = identify_idn(facility_name)

            if idn_name:
                signals.append({
                    "hospital_name_raw": facility_name,
                    "normalized_hospital_name": normalize_name(facility_name),
                    "idn_name_raw": idn_name,
                    "normalized_idn_name": normalize_name(idn_name),
                    "organization_type": ds['type'],
                    "city": city,
                    "state": state,
                    "relationship_type": rel_type,
                    "relationship_description": rel_desc,
                    "source_name": ds['name'],
                    "source_url": f"https://data.cms.gov/provider-data/dataset/{ds['id']}",
                    "source_publish_date": "2026-02-25",
                    "source_access_date": access_date,
                    "evidence_text_short": f"Name match in {ds['name']}: {facility_name} associated with {idn_name}",
                    "confidence_score": confidence,
                    "is_confirmed_idn_member": confidence >= 1.0,
                    "extraction_method": "html",
                    "notes": f"Dataset: {ds['name']}"
                })

    if signals:
        df_signals = pd.DataFrame(signals).drop_duplicates(subset=['hospital_name_raw', 'idn_name_raw'])
    else:
        df_signals = pd.DataFrame()

    # Save CSVs
    os.makedirs("data/raw/idn_public", exist_ok=True)
    df_signals.to_csv("data/raw/idn_public/idn_relationship_signals.csv", index=False)

    source_log_data = [{
        "source_name": "CMS IDN Extraction Pipeline",
        "source_url": "Multiple CMS datasets",
        "records_extracted": len(df_signals),
        "access_date": access_date
    }]
    pd.DataFrame(source_log_data).to_csv("data/raw/idn_public/idn_source_log.csv", index=False)

    if not df_signals.empty:
        df_review = df_signals[df_signals['confidence_score'] < 0.8]
    else:
        df_review = pd.DataFrame()
    df_review.to_csv("data/raw/idn_public/idn_manual_review_queue.csv", index=False)

    print(f"Total extracted {len(df_signals)} unique IDN relationship signals.")

if __name__ == "__main__":
    main()
