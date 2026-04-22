CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.hospital_340b_tic_mapping (npi TEXT, ein TEXT, billing_code TEXT, billing_code_type TEXT, negotiated_rate TEXT, negotiated_type TEXT, expiration_date TEXT, hospital_340b_id TEXT, hospital_name TEXT, ccn TEXT);
INSERT INTO raw.hospital_340b_tic_mapping VALUES ('210009', '12-3456789', '99213', 'CPT', '150.0', 'negotiated', '2025-12-31', 'DSH210009', 'JOHNS HOPKINS HOSPITAL', '210009');
