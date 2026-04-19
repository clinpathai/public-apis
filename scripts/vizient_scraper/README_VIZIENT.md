# Vizient Public Relationship Signals Scraper

This directory contains scripts to collect publicly available evidence of relationships between healthcare organizations and Vizient.

## Objective
Create an evidence-based intelligence layer identifying hospitals, health systems, and IDNs that have public signals of a relationship with Vizient (e.g., membership, renewed contracts, awards).

## What Was Collected
- **Vizient Southern States Members**: Scraped from the official member list, identifying stockholders, partners, and regional affiliates.
- **Vizient Newsroom Press Releases**: Scraped from the official newsroom, identifying new and renewed clients, expanded agreements, and partnerships.

## Why This is an Evidence Layer
This data is collected from **publicly available information only**. It is not a complete or official Vizient membership database. It serves as an evidence-based signal layer to help identify relationships where official licensed data may be missing.

## Compliance and Data Rule
- **Publicly Available Information Only**: No data was collected from behind login walls, member portals, or paid tools.
- **No Scraping Restrictions Bypassed**: The scripts respect `robots.txt` and do not attempt to bypass any technical restrictions.

## How to Rerun
1. Install dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```
2. Run the scrapers:
   ```bash
   python scripts/vizient_scraper/ss_members.py
   python scripts/vizient_scraper/newsroom_scraper.py
   ```
3. Consolidate and normalize the data:
   ```bash
   python scripts/vizient_scraper/consolidate.py
   ```

## Output Files
The following files are generated in `data/raw/vizient_public_sources/`:
- `vizient_public_relationship_signals.csv`: The consolidated evidence table.
- `vizient_source_log.csv`: A log of sources accessed.
- `vizient_manual_review_queue.csv`: Signals that require manual validation due to low confidence or ambiguous data.

## SQL Integration
The `vizient_ddl.sql` file provides the schema for loading this data into a PostgreSQL database (schemas: `raw`, `ref`, `mart`).
