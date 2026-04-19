import pandas as pd
import os
from datetime import datetime

def consolidate_vizient_data():
    raw_dir = "data/raw/vizient_public_sources/"
    ss_file = os.path.join(raw_dir, "ss_members_raw.csv")
    news_file = os.path.join(raw_dir, "newsroom_raw.csv")

    dfs = []
    if os.path.exists(ss_file):
        dfs.append(pd.read_csv(ss_file))
    if os.path.exists(news_file):
        dfs.append(pd.read_csv(news_file))

    if not dfs:
        print("No raw data found to consolidate.")
        return

    df = pd.concat(dfs, ignore_index=True)

    # Normalization logic
    def normalize_name(name):
        if not isinstance(name, str): return name
        name = name.strip()
        # Remove common suffixes/marks
        name = name.rstrip(' +*')
        return name

    df['normalized_organization_name'] = df['organization_name_raw'].apply(normalize_name)

    # Confidence score refinement
    # If is_confirmed_gpo_member is True, confidence should be 1.0
    df.loc[df['is_confirmed_gpo_member'] == True, 'confidence_score'] = 1.0

    # Deduplicate
    df = df.sort_values('confidence_score', ascending=False).drop_duplicates(subset=['normalized_organization_name', 'city', 'state'], keep='first')

    # Ensure columns order
    cols = [
        "source_name", "source_url", "source_publish_date", "source_access_date",
        "organization_name_raw", "normalized_organization_name", "organization_type",
        "city", "state", "relationship_type", "relationship_description",
        "evidence_text_short", "confidence_score", "gpo_name", "gpo_confidence",
        "is_confirmed_gpo_member", "notes", "extraction_method", "created_at"
    ]
    df = df[cols]

    # Create final deliverables
    df.to_csv(os.path.join(raw_dir, "vizient_public_relationship_signals.csv"), index=False)

    # Source Log
    source_log = df[['source_name', 'source_url', 'source_access_date']].drop_duplicates()
    source_log.to_csv(os.path.join(raw_dir, "vizient_source_log.csv"), index=False)

    # Manual Review Queue
    # Items with confidence < 0.8 or marked as uncertain_signal
    manual_review = df[(df['confidence_score'] < 0.8) | (df['relationship_type'] == 'uncertain_signal') | (df['organization_type'] == 'unknown')]
    manual_review.to_csv(os.path.join(raw_dir, "vizient_manual_review_queue.csv"), index=False)

    print(f"Consolidated {len(df)} unique signals.")
    print(f"Manual review queue contains {len(manual_review)} items.")

if __name__ == "__main__":
    consolidate_vizient_data()
