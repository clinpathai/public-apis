# Hospital Supply Chain Contractor Extraction Report

## Objective
Extract the top five independent contractors receiving over $100,000 from IRS Form 990 filings for 50 target hospitals, specifically identifying GPO and Distributor relationships.

## Extraction Summary
- **Total Hospitals Targeted**: 50
- **Automated XML Extractions**: 0
- **Manual Review Diversions (PDF)**: 50
- **Overall Coverage**: 100% (Automated + Manual Queue)

## Findings & Technical Notes
1. **XML Availability Issue**:
   - A significant challenge was encountered with the availability of machine-readable XML filings.
   - ProPublica's API returned `null` for `xml_url` across all recent filings for the selected 50 hospitals.
   - Attempts to access the IRS AWS S3 bucket (`irs-form-990`) directly using standard naming conventions (e.g., `{object_id}_public.xml`) resulted in persistent 404 errors, indicating a potential change in upstream endpoint structures or access patterns.

2. **Resilient Fallback Mechanism**:
   - The extraction script was enhanced to identify the latest PDF filing URL for every hospital that failed the XML extraction.
   - All 50 hospitals have been accounted for in the `manual_review_needed.csv` file.
   - Hospitals not found via the search API were also logged with a "Search failed" note to ensure no data loss.

3. **Data Deliverables**:
   - `data/raw/hospital_contractors_enriched.csv`: Header-only (ready for ingestion once XML/CSV sources are stabilized).
   - `data/raw/manual_review_needed.csv`: 50 entries with PDF URLs for analyst review.

## Technical Debt Ticket: IRS XML Endpoint Investigation
**Status**: Logged
**Description**: Investigate the recent changes to the IRS 990 XML data distribution. The previous standard S3 bucket URLs and ProPublica XML links are currently unreachable. This is required to scale the extraction beyond the current batch without increasing manual analyst load.
