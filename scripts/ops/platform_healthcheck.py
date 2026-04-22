import pandas as pd
import os

def run_healthcheck():
    print("--- Aplus Platform Beta Healthcheck ---")

    files_to_check = {
        "340B Mapping": "data/processed/opais_hospital_pharmacy_mapping.csv",
        "Enriched TIC Data": "data/processed/tic_hospital_rates_enriched.csv"
    }

    all_passed = True

    for label, path in files_to_check.items():
        if not os.path.exists(path):
            print(f"[FAIL] {label}: File missing at {path}")
            all_passed = False
            continue

        df = pd.read_csv(path)
        if df.empty:
            print(f"[FAIL] {label}: Dataframe is empty.")
            all_passed = False
            continue

        # Non-null validation for critical fields
        critical_cols = {
            "340B Mapping": ["hospital_340b_id", "hospital_name", "contract_pharmacy_name"],
            "Enriched TIC Data": ["npi", "negotiated_rate", "hospital_name"]
        }

        null_counts = df[critical_cols[label]].isnull().sum()
        if null_counts.sum() > 0:
            print(f"[WARN] {label}: Found null values in critical columns:")
            print(null_counts[null_counts > 0])
            all_passed = False
        else:
            print(f"[PASS] {label}: {len(df)} rows validated (Non-null check).")

    if all_passed:
        print("\nOVERALL STATUS: HEALTHY")
    else:
        print("\nOVERALL STATUS: AT RISK - Review warnings/failures.")

    return all_passed

if __name__ == "__main__":
    run_healthcheck()
