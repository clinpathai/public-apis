import pandas as pd
import os

def refine_signals(df):
    if df.empty:
        return df

    # Refine relationship types based on keywords or ownership (if we had it more explicitly)
    # For now, let's look for explicit ownership markers in the raw names

    def refine_row(row):
        hosp_name = str(row['hospital_name_raw']).upper()
        if any(marker in hosp_name for marker in [" OWNED BY ", " PART OF ", " A MEMBER OF ", " AFFILIATE OF "]):
            row['relationship_type'] = "health_system_owned"
            row['confidence_score'] = 1.0
            row['is_confirmed_idn_member'] = True

        # If it's a known major for-profit player, we can be more confident
        if row['idn_name_raw'] in ["HCA Healthcare", "Tenet Healthcare", "LifePoint Health"]:
            row['relationship_type'] = "health_system_owned"
            row['confidence_score'] = 0.9

        return row

    df = df.apply(refine_row, axis=1)
    return df

def main():
    input_file = "data/raw/idn_public/idn_relationship_signals.csv"
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    print(f"Normalizing {len(df)} signals...")

    df = refine_signals(df)

    # Save the refined signals
    df.to_csv(input_file, index=False)

    # Update manual review queue
    df_review = df[df['confidence_score'] < 0.8]
    df_review.to_csv("data/raw/idn_public/idn_manual_review_queue.csv", index=False)

    print("Normalization complete.")

if __name__ == "__main__":
    main()
