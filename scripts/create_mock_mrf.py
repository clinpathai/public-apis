import json
import os

def create_mock_mrf(file_path):
    data = {
        "reporting_entity_name": "Test Payer",
        "reporting_entity_type": "Health Insurance Company",
        "provider_references": [
            {
                "provider_group_id": 1,
                "provider_groups": [
                    {
                        "npi": ["210009"],
                        "tin": {"type": "ein", "value": "12-3456789"}
                    }
                ]
            }
        ],
        "in_network": [
            {
                "billing_code": "99213",
                "billing_code_type": "CPT",
                "negotiated_rates": [
                    {
                        "provider_references": [1],
                        "negotiated_prices": [
                            {
                                "negotiated_rate": 150.00,
                                "negotiated_type": "negotiated",
                                "expiration_date": "2025-12-31"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    create_mock_mrf("data/raw/mock_mrf.json")
    print("Mock MRF created at data/raw/mock_mrf.json")
