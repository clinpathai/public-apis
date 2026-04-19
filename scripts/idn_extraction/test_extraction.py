import pandas as pd
import os

def test_idn_signals_file_exists():
    assert os.path.exists("data/raw/idn_public/idn_relationship_signals.csv")

def test_idn_signals_content():
    df = pd.read_csv("data/raw/idn_public/idn_relationship_signals.csv")
    assert not df.empty
    assert "hospital_name_raw" in df.columns
    assert "idn_name_raw" in df.columns
    assert "source_url" in df.columns
    assert "evidence_text_short" in df.columns

    # Check if we have some expected IDNs
    idn_names = df['idn_name_raw'].unique()
    assert any("Ascension" in name for name in idn_names)
    assert any("Providence" in name for name in idn_names)

def test_idn_source_log_exists():
    assert os.path.exists("data/raw/idn_public/idn_source_log.csv")

def test_manual_review_queue_exists():
    assert os.path.exists("data/raw/idn_public/idn_manual_review_queue.csv")

if __name__ == "__main__":
    test_idn_signals_file_exists()
    test_idn_signals_content()
    test_idn_source_log_exists()
    test_manual_review_queue_exists()
    print("All IDN extraction tests passed!")
