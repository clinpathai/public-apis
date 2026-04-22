import ijson
import csv
import os
import requests
import gzip
import shutil

def parse_tic_mrf(file_path, target_npi=None, target_ein=None, output_csv="data/raw/tic_negotiated_rates.csv"):
    """
    Parses a CMS TIC Machine Readable File (MRF) using streaming to extract negotiated rates.
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    headers = [
        "npi", "ein", "billing_code", "billing_code_type",
        "negotiated_rate", "negotiated_type", "expiration_date"
    ]

    with open(output_csv, "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()

        # Open file (handle .gz if necessary)
        if file_path.endswith(".gz"):
            f_in = gzip.open(file_path, "rb")
        else:
            f_in = open(file_path, "rb")

        try:
            # CMS MRF JSON Structure Heuristic:
            # {
            #   "provider_references": [...],
            #   "in_network": [
            #     {
            #       "billing_code": "...",
            #       "negotiated_rates": [
            #         {
            #           "provider_references": [1, 2],
            #           "negotiated_prices": [{"negotiated_rate": 100, ...}]
            #         }
            #       ]
            #     }
            #   ]
            # }

            # 1. Map provider references to NPI/EIN
            provider_map = {}
            parser = ijson.parse(f_in)

            f_in.seek(0)
            items = ijson.items(f_in, 'provider_references.item')
            for item in items:
                ref_id = item.get('provider_group_id')
                providers = item.get('provider_groups', [])
                for pg in providers:
                    npi_list = pg.get('npi', [])
                    ein = pg.get('tin', {}).get('value')
                    provider_map[ref_id] = {'npis': npi_list, 'ein': ein}

            print(f"Loaded {len(provider_map)} provider references.")

            # 2. Stream in_network rates
            f_in.seek(0)
            in_network_items = ijson.items(f_in, 'in_network.item')

            for entry in in_network_items:
                billing_code = entry.get('billing_code')
                code_type = entry.get('billing_code_type')

                for rate_entry in entry.get('negotiated_rates', []):
                    refs = rate_entry.get('provider_references', [])

                    # Match by NPI/EIN if provided
                    match = False
                    current_npi = ""
                    current_ein = ""

                    if not target_npi and not target_ein:
                        match = True # Extract all if no filter
                    else:
                        for ref in refs:
                            p_info = provider_map.get(ref, {})
                            if target_npi and str(target_npi) in [str(n) for n in p_info.get('npis', [])]:
                                match = True
                                current_npi = target_npi
                                current_ein = p_info.get('ein', "")
                                break
                            if target_ein and str(target_ein) == str(p_info.get('ein', "")):
                                match = True
                                current_ein = target_ein
                                break

                    if match:
                        for price in rate_entry.get('negotiated_prices', []):
                            writer.writerow({
                                "npi": current_npi,
                                "ein": current_ein,
                                "billing_code": billing_code,
                                "billing_code_type": code_type,
                                "negotiated_rate": price.get('negotiated_rate'),
                                "negotiated_type": price.get('negotiated_type'),
                                "expiration_date": price.get('expiration_date')
                            })

        finally:
            f_in.close()

    print(f"Extraction complete. Results saved to {output_csv}")

if __name__ == "__main__":
    # Example usage (Mock)
    # parse_tic_mrf("mrf_sample.json", target_npi="1234567890")
    print("TIC MRF Parser Script Ready.")
