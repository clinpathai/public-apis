-- Healthcare Intelligence Platform Schema
-- Hierarchy: [Private Equity Firm] -> [MSO] -> [Management Entity/TIN] -> [ASC Facility/NPI]

CREATE SCHEMA IF NOT EXISTS healthcare_intel;

-- 1. Private Equity Firms
CREATE TABLE healthcare_intel.private_equity_firms (
    pe_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. MSOs (Management Services Organizations)
CREATE TABLE healthcare_intel.msos (
    mso_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    pe_firm_id INTEGER REFERENCES healthcare_intel.private_equity_firms(pe_id),
    website VARCHAR(255),
    headquarters VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Management Entities / TINs (Tax Identification Numbers)
CREATE TABLE healthcare_intel.management_entities (
    entity_id SERIAL PRIMARY KEY,
    tin CHAR(9) UNIQUE NOT NULL, -- Tax ID is typically 9 digits
    legal_name VARCHAR(255) NOT NULL,
    mso_id INTEGER REFERENCES healthcare_intel.msos(mso_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. ASC Facilities / NPIs (National Provider Identifiers)
CREATE TABLE healthcare_intel.asc_facilities (
    facility_id SERIAL PRIMARY KEY,
    npi CHAR(10) UNIQUE NOT NULL, -- NPI is 10 digits
    facility_name VARCHAR(255) NOT NULL,
    management_entity_id INTEGER REFERENCES healthcare_intel.management_entities(entity_id),
    address_line_1 VARCHAR(255),
    city VARCHAR(100),
    state CHAR(2),
    zip_code VARCHAR(10),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. TiC (Transparency in Coverage) Pricing Data Anchor
-- Linked to Management Entity via entity_id (which represents the TIN)
CREATE TABLE healthcare_intel.tic_pricing_data (
    pricing_id SERIAL PRIMARY KEY,
    management_entity_id INTEGER REFERENCES healthcare_intel.management_entities(entity_id),
    cpt_code VARCHAR(10) NOT NULL, -- Procedure code
    negotiated_rate NUMERIC(12, 2),
    billing_class VARCHAR(50), -- e.g., 'professional' or 'institutional'
    last_updated DATE,
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_mso_pe_firm ON healthcare_intel.msos(pe_firm_id);
CREATE INDEX idx_entity_mso ON healthcare_intel.management_entities(mso_id);
CREATE INDEX idx_facility_entity ON healthcare_intel.asc_facilities(management_entity_id);
CREATE INDEX idx_tic_entity ON healthcare_intel.tic_pricing_data(management_entity_id);
CREATE INDEX idx_asc_npi ON healthcare_intel.asc_facilities(npi);
CREATE INDEX idx_entity_tin ON healthcare_intel.management_entities(tin);
