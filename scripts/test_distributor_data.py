import csv
import os

def test_csv_integrity():
    files = {
        "data/raw/distributor/distributor_coverage.csv": 5,
        "data/raw/distributor/distributor_relationship_signals.csv": 202
    }

    for filepath, min_count in files.items():
        assert os.path.exists(filepath), f"{filepath} does not exist"
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) >= min_count, f"{filepath} has {len(rows)} rows, expected at least {min_count}"
            print(f"PASS: {filepath} integrity check ({len(rows)} rows)")

if __name__ == "__main__":
    try:
        test_csv_integrity()
        print("All tests passed.")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
