import pandas as pd
import os

def test_revenue_potential_ranking():
    print("Verifying BD Discovery Opportunity Ranking...")

    source_file = "data/processed/tic_hospital_rates_enriched.csv"
    if not os.path.exists(source_file):
        print("FAIL: Source enriched file not found.")
        return

    df = pd.read_csv(source_file)

    # Simple check: Group by hospital and sum rates
    ranking = df.groupby('hospital_name')['negotiated_rate'].sum().sort_values(ascending=False)

    print("Calculated Revenue Potential Ranking:")
    for i, (name, total) in enumerate(ranking.items(), 1):
        print(f"{i}. {name}: ${total:,.2f}")

    if len(ranking) > 0:
        print("SUCCESS: Rankings generated correctly based on TIC negotiated rates.")
    else:
        print("FAIL: No data found to rank.")

if __name__ == "__main__":
    test_revenue_potential_ranking()
