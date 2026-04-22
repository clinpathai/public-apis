import pandas as pd
import os

def associate_distributors(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Input file {input_path} not found.")
        return

    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading input: {e}")
        return

    if df.empty:
        print("Input CSV is empty. Creating output with headers only.")
        df = pd.DataFrame(columns=["hospital_340b_id", "hospital_name", "ccn", "contract_pharmacy_name", "pharmacy_address", "status", "effective_date", "likely_distributor"])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return

    # Mapping based on industry standards and prompt examples
    def get_distributor(pharmacy_name):
        name = str(pharmacy_name).upper()
        if "CVS" in name:
            return "McKesson"
        elif "WALGREENS" in name:
            return "Cardinal Health"
        elif "WALMART" in name or "SAMS CLUB" in name:
            return "McKesson"
        elif "RITE AID" in name:
            return "McKesson"
        elif "CARDINAL" in name:
            return "Cardinal Health"
        elif "MCKESSON" in name:
            return "McKesson"
        return "Unknown / Regional"

    df['likely_distributor'] = df['contract_pharmacy_name'].apply(get_distributor)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Enriched data saved to {output_path}")

if __name__ == "__main__":
    associate_distributors("data/raw/opais_raw_extract.csv", "data/processed/opais_hospital_pharmacy_mapping.csv")
