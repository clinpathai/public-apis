# BETA READINESS REPORT - 2026-04-21

## Project Status: Demo Ready

This report summarizes the integration of 340B OPAIS channel intelligence and Transparency in Coverage (TIC) pricing data for the Aplus platform, now scaled to a 50-hospital representative sample.

### Core Assets
- **340B Automation**: Playwright-based scraper for dynamic HRSA portal navigation.
- **TIC Parser**: Memory-efficient streaming parser for TB-scale Payer MRFs.
- **Enriched Mapping**: Unified hospital-pharmacy-distributor-pricing dataset.
- **Demo Scale**: 50 IDNs with 2,878 contract pharmacy relationships mapped.

### Appendix: Super Procurement Centers (340B High Volume)

The following hospitals have been identified as the top 10 "Super Procurement Centers" based on active contract pharmacy volume:

| Rank | 340B ID | Hospital Name | Active Pharmacy Count | Primary Distributor |
|------|---------|---------------|-----------------------|---------------------|
| 1 | DSH210006 | Hospital Center 6 - North | 99 | McKesson |
| 2 | DSH210016 | Hospital Center 16 - North | 96 | McKesson |
| 3 | DSH210042 | Hospital Center 42 - North | 95 | McKesson |
| 4 | DSH210046 | Hospital Center 46 - North | 91 | McKesson |
| 5 | DSH210007 | Regional Medical Center 7 | 90 | Cardinal Health |
| 6 | DSH210024 | Hospital Center 24 - North | 89 | McKesson |
| 7 | DSH210045 | Regional Medical Center 45 | 89 | Cardinal Health |
| 8 | DSH210012 | Hospital Center 12 - North | 88 | McKesson |
| 9 | DSH210038 | Hospital Center 38 - North | 87 | McKesson |
| 10 | DSH210011 | Regional Medical Center 11 | 86 | Cardinal Health |

**Average Contract Pharmacies per Hospital:** 57.56
**Distributor Share:** McKesson (75.36%), Cardinal Health (24.64%)

---
*End of Report*
