import json
import pandas as pd
import random

def generate_bulk_demo_data(count=50):
    print(f"Generating bulk demo data for {count} hospitals...")

    hospitals = []
    tic_rates = []
    opais_data = []

    for i in range(1, count + 1):
        hospital_id = f"DSH{210000 + i}"
        ccn = f"{210000 + i}"
        name = f"Hospital Center {i} - North" if i % 2 == 0 else f"Regional Medical Center {i}"

        hospitals.append({
            "hospital_340b_id": hospital_id,
            "hospital_name": name,
            "ccn": ccn
        })

        # OPAIS Contract Pharmacies for this hospital
        pharm_count = random.randint(5, 100)
        for j in range(pharm_count):
            opais_data.append({
                "hospital_340b_id": hospital_id,
                "hospital_name": name,
                "ccn": ccn,
                "contract_pharmacy_name": random.choice(["CVS Pharmacy", "Walgreens", "Rite Aid", "Walmart Pharmacy"]),
                "pharmacy_address": f"{random.randint(100, 999)} Main St, City {i}",
                "status": "Active",
                "effective_date": "2020-01-01"
            })

        # TIC Negotiated Rates for this hospital
        rate = random.uniform(100.0, 5000.0)
        tic_rates.append({
            "npi": ccn, # Simplified NPI=CCN for join
            "ein": f"00-{random.randint(1000000, 9999999)}",
            "billing_code": "99213",
            "billing_code_type": "CPT",
            "negotiated_rate": round(rate, 2),
            "negotiated_type": "negotiated",
            "expiration_date": "2025-12-31"
        })

    # Save to raw files
    pd.DataFrame(opais_data).to_csv("data/raw/opais_raw_extract.csv", index=False)
    pd.DataFrame(tic_rates).to_csv("data/raw/tic_negotiated_rates.csv", index=False)

    print("Bulk demo data generated in data/raw/")

if __name__ == "__main__":
    generate_bulk_demo_data(50)
