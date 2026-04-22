import pandas as pd
import os

def associate_tic_340b(tic_csv, opais_csv, output_csv="data/processed/tic_hospital_rates_enriched.csv"):
    if not os.path.exists(tic_csv) or not os.path.exists(opais_csv):
        print("Required CSV files for association not found.")
        return

    tic_df = pd.read_csv(tic_csv)
    opais_df = pd.read_csv(opais_csv)

    # We associate based on CCN/NPI matching if possible.
    # For now, we align TIC NPI (mocked as CCN for Vanderbilt) with OPAIS hospital data.
    # In a real scenario, we'd have an NPI-CCN-340BID crosswalk.

    # Heuristic join: Assume NPI in TIC matches Hospital CCN (or we have a crosswalk)
    # Vanderbilt Vanderbilt CCN: 440039, Johns Hopkins: 210009

    # Ensure ID formats match
    tic_df['npi'] = tic_df['npi'].astype(str)
    opais_df['ccn'] = opais_df['ccn'].astype(str)

    # Join on Hospital ID if mapped, or name
    enriched_df = pd.merge(
        tic_df,
        opais_df[['hospital_340b_id', 'hospital_name', 'ccn']].drop_duplicates(),
        left_on='npi',
        right_on='ccn',
        how='inner'
    )

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    enriched_df.to_csv(output_csv, index=False)
    print(f"Data association complete. Enriched TIC data saved to {output_csv}")

if __name__ == "__main__":
    associate_tic_340b("data/raw/tic_negotiated_rates.csv", "data/raw/opais_raw_extract.csv")
