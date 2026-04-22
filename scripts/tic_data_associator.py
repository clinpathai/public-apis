import pandas as pd
import os
import shutil

def associate_tic_340b(tic_csv, opais_mapping_csv, output_csv="data/processed/tic_hospital_rates_enriched.csv"):
    if not os.path.exists(tic_csv) or not os.path.exists(opais_mapping_csv):
        print("Required CSV files for association not found.")
        return

    tic_df = pd.read_csv(tic_csv)
    # This now contains hospital info + pharmacy names + distributors
    opais_df = pd.read_csv(opais_mapping_csv)

    print(f"Joining TIC ({len(tic_df)} rows) with OPAIS/Pharmacy Mapping ({len(opais_df)} rows)...")

    # Ensure ID formats match for join
    tic_df['npi'] = tic_df['npi'].astype(str)
    opais_df['ccn'] = opais_df['ccn'].astype(str)

    # Join on Hospital ID (NPI = CCN)
    # This expands the dataset to show negotiated pricing PER contract pharmacy
    enriched_df = pd.merge(
        tic_df,
        opais_df,
        left_on='npi',
        right_on='ccn',
        how='inner'
    )

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    enriched_df.to_csv(output_csv, index=False)

    # Also overwrite the 'enriched_hospital_mapping.csv' used by the ETL script
    shutil_path = "data/processed/enriched_hospital_mapping.csv"
    enriched_df.to_csv(shutil_path, index=False)

    print(f"Data association complete. Enriched TIC data (with pharmacies) saved to {output_csv}")
    print(f"Dataset now contains {len(enriched_df)} mappings.")

if __name__ == "__main__":
    associate_tic_340b("data/raw/tic_negotiated_rates.csv", "data/processed/opais_hospital_pharmacy_mapping.csv")
