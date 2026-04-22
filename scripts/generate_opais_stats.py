import pandas as pd
import os

def generate_stats(csv_path):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)

    if df.empty:
        print("No data available to generate stats.")
        return

    # 1. Average number of contract pharmacies per hospital
    pharmacy_counts = df.groupby('hospital_340b_id')['contract_pharmacy_name'].count()
    avg_pharmacies = pharmacy_counts.mean()

    # 2. Top 10 "Super Procurement Centers"
    top_10 = df.groupby(['hospital_340b_id', 'hospital_name']).size().reset_index(name='pharmacy_count')
    top_10 = top_10.sort_values(by='pharmacy_count', ascending=False).head(10)

    # 3. Distributor Distribution Report
    dist_report = df['likely_distributor'].value_counts().reset_index()
    dist_report.columns = ['distributor', 'count']
    dist_report['percentage'] = (dist_report['count'] / dist_report['count'].sum() * 100).round(2)

    print("--- 340B OPAIS CHANNEL INTELLIGENCE SUMMARY ---")
    print(f"Average contract pharmacies per hospital: {avg_pharmacies:.2f}")
    print("\nTop 10 Super Procurement Centers:")
    print(top_10.to_string(index=False))
    print("\nDistributor Distribution:")
    print(dist_report.to_string(index=False))

    # Save stats to a text file
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/opais_summary_stats.txt", "w") as f:
        f.write("--- 340B OPAIS CHANNEL INTELLIGENCE SUMMARY ---\n")
        f.write(f"Average contract pharmacies per hospital: {avg_pharmacies:.2f}\n")
        f.write("\nTop 10 Super Procurement Centers:\n")
        f.write(top_10.to_string(index=False))
        f.write("\n\nDistributor Distribution:\n")
        f.write(dist_report.to_string(index=False))

if __name__ == "__main__":
    generate_stats("data/processed/opais_hospital_pharmacy_mapping.csv")
