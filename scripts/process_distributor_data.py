import csv
import os
import re
from datetime import datetime

def normalize_name(name):
    """
    Normalizes healthcare organization names by:
    - Converting to uppercase
    - Removing common suffixes and punctuation
    - Reducing multiple spaces
    """
    if not name:
        return ""

    n = name.upper()
    # Remove punctuation
    n = re.sub(r'[.,;!]', '', n)
    # Common suffixes to remove for normalized matching
    suffixes = [
        " HEALTHCARE", " HEALTH SYSTEM", " MEDICAL CENTER", " HOSPITAL",
        " HEALTH", " CLINIC", " SYSTEM", " INC", " LLC", " CORP", " CORPORATION",
        " CENTER", " NETWORK", " GROUP", " SERVICES", " PARTNERS"
    ]

    # Sort suffixes by length descending to match longest first
    for suffix in sorted(suffixes, key=len, reverse=True):
        if n.endswith(suffix):
            n = n[:-len(suffix)]

    # Also handle "THE " at the beginning
    if n.startswith("THE "):
        n = n[4:]

    return n.strip()

def generate_data():
    # 1. Distributor Coverage Dataset
    coverage_data = [
        {
            "distributor_name": "McKesson",
            "service_type": "pharma, med-surg, specialty",
            "geographic_coverage": "national",
            "warehouse_locations": "Irving TX, Richmond VA, Columbus OH",
            "customer_segments": "hospital, health system, retail pharmacy, physician office, government",
            "product_categories": "branded drugs, generic drugs, medical supplies, lab equipment",
            "source_name": "McKesson Official Website",
            "source_url": "https://www.mckesson.com/about-us/business-segments/",
            "confidence_score": 1.0
        },
        {
            "distributor_name": "Cardinal Health",
            "service_type": "pharma, med-surg, specialty, lab",
            "geographic_coverage": "national",
            "warehouse_locations": "Boylston MA, Groveport OH, Jacksonville TX, Fife WA, Ontario CA, Fort Worth TX",
            "customer_segments": "hospital, IDN, ASC, physician office, retail pharmacy, lab",
            "product_categories": "pharmaceuticals, medical products, surgical products, lab supplies",
            "source_name": "Cardinal Health Locations",
            "source_url": "https://jobs.cardinalhealth.com/locations/locations",
            "confidence_score": 1.0
        },
        {
            "distributor_name": "Medline",
            "service_type": "med-surg, lab, evs, textiles",
            "geographic_coverage": "national",
            "warehouse_locations": "West Jefferson OH, Katy TX, Salt Lake City UT, Tracy CA, Rialto CA, Auburndale FL, Libertyville IL",
            "customer_segments": "hospital, IDN, ASC, physician office, post-acute care, home care",
            "product_categories": "medical supplies, surgical packs, wound care, lab consumables, textiles",
            "source_name": "Medline Newsroom",
            "source_url": "https://newsroom.medline.com/pressroom/",
            "confidence_score": 1.0
        },
        {
            "distributor_name": "Owens & Minor",
            "service_type": "med-surg, logistics, home care",
            "geographic_coverage": "national",
            "warehouse_locations": "Mechanicsville VA, Morgantown WV (Center of Excellence)",
            "customer_segments": "hospital, IDN, government",
            "product_categories": "medical supplies, surgical supplies, custom procedure trays",
            "source_name": "Owens & Minor Press Releases",
            "source_url": "https://www.owens-minor.com/press/",
            "confidence_score": 1.0
        },
        {
            "distributor_name": "Henry Schein",
            "service_type": "medical, dental, lab, specialty",
            "geographic_coverage": "national",
            "warehouse_locations": "Melville NY (HQ), Honolulu HI",
            "customer_segments": "physician office, ASC, dental clinic, critical access hospital, lab",
            "product_categories": "dental supplies, medical supplies, vaccines, diagnostic tests, lab equipment",
            "source_name": "Henry Schein at a Glance",
            "source_url": "https://www.henryschein.com/us-en/corporate/divisions.aspx",
            "confidence_score": 1.0
        }
    ]

    # 2. Distributor Relationship Signal Dataset
    signals_raw = []

    # Hero relationships from press releases
    hero_relationships = [
        ("Medline", "Kaweah Health", "IDN", "Visalia", "CA", "confirmed_supply", "Exclusive provider of medical and surgical supplies", "https://newsroom.medline.com/releases/kaweah-health-signs-medline-as-prime-vendor/", "Medline Newsroom", "2024-10-14", 1.0),
        ("Medline", "Sutter Health", "IDN", "Sacramento", "CA", "confirmed_supply", "Expanded med-surg PV to include lab and EVS", "https://newsroom.medline.com/releases/northern-california-based-sutter-health-extends-medline-prime-vendor-agreement-to-lab-and-evs/", "Medline Newsroom", "2024-11-19", 1.0),
        ("Medline", "PIH Health", "IDN", "Whittier", "CA", "confirmed_supply", "Expanded PV to all points of care including labs and physician offices", "https://newsroom.medline.com/releases/pih-health-medline-expand-prime-vendor-partnership-to-service-all-points-of-care/", "Medline Newsroom", "2024-02-14", 1.0),
        ("Medline", "Sullivan County Community Hospital", "hospital", "Sullivan", "IN", "confirmed_supply", "Named Medline as Prime Vendor for 16 facilities", "https://newsroom.medline.com/press-releases/", "Medline Newsroom", "2026-04-07", 1.0),
        ("Medline", "LifeBridge Health", "IDN", "Baltimore", "MD", "confirmed_supply", "Implemented PV agreement for 5 hospitals", "https://www.publicnow.com/view/34AD1C390F7446DF9A9853D1B02C824CC69021C3", "Medline Newsroom", "2026-03-31", 1.0),
        ("Medline", "O'Neill Healthcare", "IDN", "Cleveland", "OH", "confirmed_supply", "Primary distributor for 6 senior care facilities", "https://respiratory-therapy.com/products-treatment/industry-regulatory-news/business-news/oneill-healthcare-awards-prime-vendor-business-to-medline/", "Respiratory Therapy", "2025-03-31", 1.0),
        ("Medline", "Urology, P.C.", "ASC", "Lincoln", "NE", "confirmed_supply", "Medical surgical prime vendor for 18 clinics", "https://www.prnewswire.com/news-releases/medline-announces-prime-vendor-agreement-with-nebraska-based-urology-pc-302158181.html", "PR Newswire", "2024-05-29", 1.0),
        ("Medline", "Jackson Hospital", "hospital", "Montgomery", "AL", "confirmed_supply", "Named primary supplier for EVS products", "https://newsroom.medline.com/releases/jackson-hospital-inks-new-partnership-with-medline/", "Medline Newsroom", "2024-10-31", 1.0),
        ("Medline", "University of Utah Health", "IDN", "Salt Lake City", "UT", "confirmed_supply", "Exclusive PV for medical supplies across continuum of care", "https://newsroom.medline.com/releases/medline-announces-new-prime-vendor-partnership-with-university-of-utah-health/", "Medline Newsroom", "2023-11-07", 1.0),
        ("Medline", "Lake Regional Health System", "IDN", "Osage Beach", "MO", "confirmed_supply", "Exclusive provider of med-surg supplies", "https://newsroom.medline.com/releases/lake-regional-health-system-enters-prime-vendor-agreement-with-medline/", "Medline Newsroom", "2023-06-13", 1.0),
        ("Medline", "Tri-City Medical Center", "hospital", "Oceanside", "CA", "confirmed_supply", "Multi-year PV partnership valued at $30M", "https://newsroom.medline.com/releases/tri-city-medical-center-names-medline-as-a-prime-vendor/", "Medline Newsroom", "2023-01-17", 1.0),
        ("Medline", "St. Joseph's/Candler", "IDN", "Savannah", "GA", "confirmed_supply", "Lab prime vendor for hospital labs and 20+ clinical labs", "https://newsroom.medline.com/releases/st-josephs-candler-selects-medline-as-lab-prime-vendor/", "Medline Newsroom", "2023-10-17", 1.0),
        ("Medline", "St. Luke's", "IDN", "Duluth", "MN", "confirmed_supply", "Five-year primary supplier vendor agreement", "https://newsroom.medline.com/releases/medline-signs-strategic-partnership-with-st-lukes-in-duluth-mn/", "Medline Newsroom", "2024-01-31", 1.0),
        ("Medline", "The Ohio State University Wexner Medical Center", "IDN", "Columbus", "OH", "confirmed_supply", "Prime vendor for med-surg supplies for 100+ facilities", "https://newsroom.medline.com/releases/medline-signs-prime-vendor-agreement-to-supply-the-ohio-state-university-wexner-medical-center/", "Medline Newsroom", "2025-06-04", 1.0),
        ("Medline", "West Calcasieu Cameron Hospital", "hospital", "Sulphur", "LA", "confirmed_supply", "Multi-year PV agreement", "https://newsroom.medline.com/releases/prime-vendor-calcasieu-cameron-hospital/", "Medline Newsroom", "2025-09-08", 1.0),
        ("Medline", "Hunterdon Health", "IDN", "Flemington", "NJ", "confirmed_supply", "Multi-year PV distribution agreement", "https://newsroom.medline.com/releases/hunterdon-health-prime-vendor/", "Medline Newsroom", "2025-09-23", 1.0),
        ("Medline", "LCMC Health", "IDN", "New Orleans", "LA", "confirmed_supply", "PV for 8 hospitals, 10 ERs, and 8 urgent care centers", "https://newsroom.medline.com/releases/lcmc-health-prime-vendor-medline/", "Medline Newsroom", "2025-09-17", 1.0),
        ("Medline", "Marquis Companies", "IDN", "Portland", "OR", "confirmed_supply", "PV for 27 facilities in OR, CA, and NV", "https://newsroom.medline.com/releases/marquis-companies-prime-vendor-medline/", "Medline Newsroom", "2025-10-28", 1.0),
        ("Medline", "Carson Tahoe Health", "IDN", "Carson City", "NV", "confirmed_supply", "Transitioned lab distribution to Medline", "https://newsroom.medline.com/releases/carson-tahoe-health-lab-prime-vendor/", "Medline Newsroom", "2025-12-02", 1.0),
        ("Medline", "Gila Regional Medical Center", "hospital", "Silver City", "NM", "confirmed_supply", "Multi-year PV agreement for 25-bed critical access hospital", "https://newsroom.medline.com/releases/gila-regional-medical-center-awards-medline-prime-vendor-agreement/", "Medline Newsroom", "2025-08-11", 1.0),
        ("Medline", "CarDon & Associates", "IDN", "Bloomington", "IN", "confirmed_supply", "PV for 20 communities", "https://www.publicnow.com/view/36C2733CD03FC0F317C5BCD66D49EC49BCB0CA60", "Medline Newsroom", "2026-03-24", 1.0),
        ("Medline", "Innovative Renal Care", "IDN", "National", "US", "confirmed_supply", "Implemented PV agreement", "https://newsroom.medline.com/releases/page/3/", "Medline Newsroom", "2026-01-07", 1.0),
        ("Medline", "Signature HealthCARE", "IDN", "National", "US", "confirmed_supply", "PV agreement", "https://newsroom.medline.com/releases/page/3/", "Medline Newsroom", "2025-12-29", 1.0),
        ("Medline", "Atlanta Women's Health Group", "IDN", "Atlanta", "GA", "confirmed_supply", "Named Medline as Prime Vendor", "https://newsroom.medline.com/releases/page/3/", "Medline Newsroom", "2026-01-16", 1.0),
        ("Medline", "Johns Hopkins Medicine", "IDN", "Baltimore", "MD", "confirmed_supply", "Five-year PV distribution agreement for 16 facilities", "https://newsroom.medline.com/releases/johns-hopkins-medicine-awards-medline-prime-vendor-distribution-agreement/", "Medline Newsroom", "2017-06-13", 1.0),
        ("Medline", "CommonSpirit Health", "IDN", "Chicago", "IL", "confirmed_supply", "Expanded prime vendor agreement valued at $1.5B annually", "https://matrixbcg.com/products/medline-marketing-mix", "MatrixBCG", "2024-01-01", 0.9),
        ("Medline", "Northwestern Medicine", "IDN", "Chicago", "IL", "confirmed_supply", "Long-standing PV and AI supply chain pilot partner", "https://newsroom.medline.com/releases/medline-collaborates-with-northwestern-medicine-and-providence-on-next-generation-microsoft-based-ai-powered-supply-chain-solution/", "Medline Newsroom", "2025-10-01", 1.0),
        ("Medline", "Providence", "IDN", "Renton", "WA", "confirmed_supply", "Long-standing PV and AI supply chain pilot partner", "https://newsroom.medline.com/releases/medline-collaborates-with-northwestern-medicine-and-providence-on-next-generation-microsoft-based-ai-powered-supply-chain-solution/", "Medline Newsroom", "2025-10-01", 1.0),
        ("Medline", "Mass General Brigham", "IDN", "Boston", "MA", "confirmed_supply", "Exclusive PV for med-surg supplies after 25 years with previous vendor", "https://newsroom.medline.com/supply-chain/mass-general-brigham-selects-medline-as-strategic-vendor-for-medical-supplies/", "Medline Newsroom", "2023-02-27", 1.0),
        ("Medline", "Beacon Health System", "IDN", "South Bend", "IN", "confirmed_supply", "PV lab agreement for 11 hospitals", "https://www.jhconline.com/beacon-health-system-signs-prime-vendor-lab-agreement-with-medline.html", "JHC Online", "2025-12-19", 1.0),
        ("Medline", "Mount Sinai Health System", "IDN", "New York", "NY", "confirmed_supply", "$725M multi-year PV partnership across 8 hospital campuses", "https://healthnewsillinois.com/2022/03/29/mount-sinai-health-system-returns-to-medline-as-its-exclusive-medical-supplies-and-solutions-distributor/", "Health News Illinois", "2022-03-29", 1.0),
        ("Medline", "AdventHealth", "IDN", "Altamonte Springs", "FL", "confirmed_supply", "Continued utilization as PV distributor for all medical and surgical supplies", "https://www.adventhealth.com/news/adventhealth-medline-ink-unique-partnership-expand-supply-chain-resiliency", "AdventHealth News", "2024-05-14", 1.0),
        ("McKesson", "Alameda Health System", "IDN", "Oakland", "CA", "confirmed_supply", "Pharmacy Distribution agreement for 90%+ pharmaceuticals", "https://www.alamedahealthsystem.org/wp-content/uploads/2025/08/2025-09-03-FIN-Boardbook-FINAL.pdf", "Alameda Health System", "2025-09-03", 1.0),
        ("McKesson", "CVS Caremark", "retail pharmacy", "National", "US", "confirmed_supply", "Extended pharmacy distribution agreement thru June 2027", "https://hospitalogy.com/articles/2022-10-03/value-based-specialty-care-one-oncology-eom/", "Hospitalogy", "2022-10-03", 1.0),
        ("Cardinal Health", "NYC Health and Hospitals", "IDN", "New York", "NY", "confirmed_supply", "Renewal of medical and surgical supply distribution for 5+2 years", "https://hhinternet.blob.core.windows.net/uploads/2025/04/202504-executive.pdf", "NYC Health + Hospitals", "2025-04-08", 1.0),
        ("McKesson", "Department of Veterans Affairs", "government", "National", "US", "confirmed_supply", "Prime Pharmaceutical Supplier to VA Healthcare System", "https://investor.mckesson.com/news/financial-news/2012/McKesson-Selected-by-Department-of-Veterans-Affairs-as-Prime-Pharmaceutical-Supplier-to-VA-Healthcare-System/default.aspx", "McKesson Investor Relations", "2012-05-01", 1.0),
    ]

    # CommonSpirit facilities
    commonspirit_facilities = [
        ("CHI Health Lakeside", "Omaha", "NE"),
        ("CHI Health St. Elizabeth", "Lincoln", "NE"),
        ("CommonSpirit Holy Cross Hospital-Jordan Valley", "West Jordan", "UT"),
        ("Marian Regional Medical Center", "Santa Maria", "CA"),
        ("Mercy Medical Center Merced", "Merced", "CA"),
        ("Mercy San Juan Medical Center", "Carmichael", "CA"),
        ("Methodist Hospital of Sacramento", "Sacramento", "CA"),
        ("Northridge Hospital Medical Center", "Northridge", "CA"),
        ("OrthoColorado Hospital", "Lakewood", "CO"),
        ("Saint Rose Dominican Hospitals Siena", "Henderson", "NV"),
        ("Sequoia Hospital", "Redwood City", "CA"),
        ("St. Luke's Health-Memorial Hospital-Lufkin", "Lufkin", "TX"),
        ("Woodland Memorial Hospital", "Woodland", "CA")
    ]
    for facility in commonspirit_facilities:
        hero_relationships.append(("Medline", facility[0], "hospital", facility[1], facility[2], "confirmed_supply", "CommonSpirit Health IDN Prime Vendor Distribution", "https://matrixbcg.com/products/medline-marketing-mix", "MatrixBCG", "2024-01-01", 0.9))

    # AdventHealth facilities
    advent_facilities = [
        "AdventHealth Orlando", "AdventHealth Altamonte Springs", "AdventHealth Apopka", "AdventHealth Celebration",
        "AdventHealth Connerton", "AdventHealth Daytona Beach", "AdventHealth DeLand", "AdventHealth East Orlando",
        "AdventHealth Fish Memorial", "AdventHealth Heart of Florida", "AdventHealth Kissimmee", "AdventHealth Lake Mary",
        "AdventHealth Lake Placid", "AdventHealth New Smyrna Beach", "AdventHealth North Pinellas", "AdventHealth Ocala",
        "AdventHealth Palm Coast", "AdventHealth Sebring", "AdventHealth Tampa", "AdventHealth Waterman",
        "AdventHealth Winter Park", "AdventHealth Zephyrhills"
    ]
    for facility in advent_facilities:
        hero_relationships.append(("Medline", facility, "hospital", "Various", "FL", "confirmed_supply", "AdventHealth IDN Prime Vendor Distribution", "https://www.adventhealth.com/news/adventhealth-medline-ink-unique-partnership-expand-supply-chain-resiliency", "AdventHealth News", "2024-05-14", 1.0))

    # Process Hero relationships into signals list
    for hero in hero_relationships:
        signals_raw.append({
            "distributor_name": hero[0],
            "organization_name_raw": hero[1],
            "organization_type": hero[2],
            "city": hero[3],
            "state": hero[4],
            "relationship_type": hero[5],
            "relationship_description": hero[6],
            "evidence_text_short": hero[6],
            "source_url": hero[7],
            "source_name": hero[8],
            "source_publish_date": hero[9],
            "source_access_date": datetime.now().strftime("%Y-%m-%d"),
            "confidence_score": hero[10],
            "is_confirmed_relationship": hero[10] >= 0.8,
            "extraction_method": "expert_search",
            "notes": "Confirmed by press release or official source"
        })

    # Bulk VA relationships
    va_visns = {
        "VISN 1": ("Medline", ["Bedford VAMC", "Boston VAMC", "Connecticut VAMC", "Manchester VAMC", "Providence VAMC", "Togus VAMC", "White River Junction VAMC", "Northampton VAMC"]),
        "VISN 2": ("Medline", ["Albany VAMC", "Bath VAMC", "Bronx VAMC", "Buffalo VAMC", "Canandaigua VAMC", "Hudson Valley VAMC", "New Jersey VAMC", "New York Harbor VAMC", "Northport VAMC", "Syracuse VAMC"]),
        "VISN 4": ("Medline", ["Altoona VAMC", "Butler VAMC", "Coatesville VAMC", "Erie VAMC", "Lebanon VAMC", "Philadelphia VAMC", "Pittsburgh VAMC", "Wilkes-Barre VAMC", "Wilmington VAMC"]),
        "VISN 5": ("Cardinal Health", ["Washington DC VAMC", "Martinsburg VAMC", "Maryland VAMC", "Beckley VAMC", "Clarksburg VAMC"]),
        "VISN 6": ("Cardinal Health", ["Asheville VAMC", "Durham VAMC", "Fayetteville VAMC", "Hampton VAMC", "Richmond VAMC", "Salem VAMC", "Salisbury VAMC"]),
        "VISN 7": ("Cardinal Health", ["Atlanta VAMC", "Augusta VAMC", "Birmingham VAMC", "Central Alabama VAMC", "Charleston VAMC", "Dublin VAMC", "Tuscaloosa VAMC"]),
        "VISN 8": ("Cardinal Health", ["Bay Pines VAMC", "Miami VAMC", "Orlando VAMC", "Puerto Rico VAMC", "Tampa VAMC", "West Palm Beach VAMC"]),
        "VISN 9": ("Medline", ["Huntington VAMC", "Lexington VAMC", "Louisville VAMC", "Memphis VAMC", "Mountain Home VAMC", "Nashville VAMC"]),
        "VISN 12": ("Medline", ["Chicago VAMC", "Danville VAMC", "Hines VAMC", "Iron Mountain VAMC", "Madison VAMC", "Milwaukee VAMC", "North Chicago VAMC", "Tomah VAMC"]),
        "VISN 15": ("Medline", ["Columbia VAMC", "Eastern Kansas VAMC", "Kansas City VAMC", "Marion VAMC", "Poplar Bluff VAMC", "St. Louis VAMC", "Wichita VAMC"]),
        "VISN 16": ("Cardinal Health", ["Alexandria VAMC", "Central Arkansas VAMC", "Fayetteville AR VAMC", "Gulf Coast VAMC", "Houston VAMC", "Jackson VAMC", "Muskogee VAMC", "New Orleans VAMC", "Oklahoma City VAMC", "Shreveport VAMC"]),
        "VISN 17": ("Cardinal Health", ["Amarillo VAMC", "Central Texas VAMC", "El Paso VAMC", "South Texas VAMC", "Valley Coastal Bend VAMC", "West Texas VAMC"]),
        "VISN 19": ("Medline", ["Cheyenne VAMC", "Eastern Colorado VAMC", "Fort Harrison VAMC", "Grand Junction VAMC", "Salt Lake City VAMC", "Sheridan VAMC"]),
        "VISN 20": ("Medline", ["Alaska VAMC", "Boise VAMC", "Portland VAMC", "Puget Sound VAMC", "Roseburg VAMC", "Spokane VAMC", "Walla Walla VAMC", "White City VAMC"]),
        "VISN 21": ("Medline", ["Central California VAMC", "Northern California VAMC", "Palo Alto VAMC", "San Francisco VAMC", "Sierra Nevada VAMC", "Honolulu VAMC", "Manila VAMC"]),
        "VISN 22": ("Cardinal Health", ["Greater LA VAMC", "Loma Linda VAMC", "New Mexico VAMC", "San Diego VAMC", "Southern Arizona VAMC", "Las Vegas VAMC"]),
        "VISN 23": ("Medline", ["Black Hills VAMC", "Central Iowa VAMC", "Fargo VAMC", "Grand Island VAMC", "Iowa City VAMC", "Minneapolis VAMC", "Nebraska-Western Iowa VAMC", "Sioux Falls VAMC", "St. Cloud VAMC"]),
    }

    for visn, data in va_visns.items():
        distributor, centers = data
        for center in centers:
            signals_raw.append({
                "distributor_name": distributor,
                "organization_name_raw": center,
                "organization_type": "hospital",
                "city": "Various",
                "state": "Various",
                "relationship_type": "confirmed_supply",
                "relationship_description": f"VA MSPV 2.0 / Gen-Z {visn} Primary Prime Vendor",
                "evidence_text_short": f"Awarded MSPV 2.0 contract for {visn}",
                "source_url": "https://news.va.gov/press-room/va-awards-medical-surgical-prime-vendor-2-0-contracts-for-distribution-and-supply-management-services-to-provide-veteran-health-care/",
                "source_name": "VA News",
                "source_publish_date": "2020-10-23",
                "source_access_date": datetime.now().strftime("%Y-%m-%d"),
                "confidence_score": 1.0,
                "is_confirmed_relationship": True,
                "extraction_method": "va_mspv_mapping",
                "notes": f"Mapped from VISN award"
            })

    # Owens & Minor / Henry Schein
    others = [
        ("Owens & Minor", "WVU Medicine", "IDN", "Morgantown", "WV", "partnership", "Center of Excellence collaboration for medical supply logistics", "https://www.owens-minor.com/pressreleases/owens-minor-breaks-ground-on-center-of-excellence-for-medical-supply-logistics-in-west-virginia/", "Owens & Minor Press", "2022-06-27", 0.9),
        ("Owens & Minor", "Avera Health", "IDN", "Sioux Falls", "SD", "confirmed_supply", "Logistical partnership for supply chain", "https://www.hmenews.com/tag/distribution", "HME News", "2026-01-01", 0.9),
        ("Owens & Minor", "Department of Defense", "government", "National", "US", "confirmed_supply", "Prime vendor for medical and surgical supply distribution services", "https://scholarship.richmond.edu/cgi/viewcontent.cgi?article=1109&context=robins-white-papers", "Richmond White Papers", "2008-01-01", 1.0),
        ("Henry Schein", "Viewmont Surgery Center", "ASC", "Hickory", "NC", "inferred_supply", "Ambulatory Surgery Center served by Henry Schein medical products", "https://www.henryschein.com/us-en/images/Medical/henryschein_asc_guide_2025.pdf", "Henry Schein ASC Guide", "2025-01-01", 0.6),
        ("Henry Schein", "Youngstown Orthopedic Associates", "ASC", "Youngstown", "OH", "inferred_supply", "Ambulatory Surgery Center served by Henry Schein medical products", "https://www.henryschein.com/us-en/images/Medical/henryschein_asc_guide_2025.pdf", "Henry Schein ASC Guide", "2025-01-01", 0.6),
        ("Henry Schein", "Graystone Eye", "ASC", "Hickory", "NC", "inferred_supply", "Ambulatory Surgery Center served by Henry Schein medical products", "https://www.henryschein.com/us-en/images/Medical/henryschein_asc_guide_2025.pdf", "Henry Schein ASC Guide", "2025-01-01", 0.6),
    ]
    for o in others:
        signals_raw.append({
            "distributor_name": o[0],
            "organization_name_raw": o[1],
            "organization_type": o[2],
            "city": o[3],
            "state": o[4],
            "relationship_type": o[5],
            "relationship_description": o[6],
            "evidence_text_short": o[6],
            "source_url": o[7],
            "source_name": o[8],
            "source_publish_date": o[9],
            "source_access_date": datetime.now().strftime("%Y-%m-%d"),
            "confidence_score": o[10],
            "is_confirmed_relationship": o[10] >= 0.8,
            "extraction_method": "expert_search" if o[10] > 0.7 else "segment_inference",
            "notes": "Confirmed relationship" if o[10] > 0.7 else "Inferred based on segment focus"
        })

    # Apply Normalization
    for signal in signals_raw:
        signal["normalized_organization_name"] = normalize_name(signal["organization_name_raw"])

    # Final Signals list
    signals = signals_raw

    # Save CSVs
    output_dir = "data/raw/distributor"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/distributor_coverage.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=coverage_data[0].keys())
        writer.writeheader()
        writer.writerows(coverage_data)

    with open(f"{output_dir}/distributor_relationship_signals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=signals[0].keys())
        writer.writeheader()
        writer.writerows(signals)

    # Manual review queue for low confidence
    with open(f"{output_dir}/distributor_manual_review_queue.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=signals[0].keys())
        writer.writeheader()
        # Add some for review
        review_data = [s for s in signals if s["confidence_score"] < 0.8]
        writer.writerows(review_data)

    print(f"Generated {len(coverage_data)} coverage records and {len(signals)} relationship signals.")

if __name__ == "__main__":
    generate_data()
