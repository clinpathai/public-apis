-- Database: aplus_health_intel
-- Schema setup for Distributor Intelligence

CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS mart;

-- 1. Distributor Coverage Table
CREATE TABLE IF NOT EXISTS ref.distributor_coverage (
    distributor_id BIGSERIAL PRIMARY KEY,
    distributor_name TEXT,
    service_type TEXT,
    geographic_coverage TEXT,
    warehouse_locations TEXT,
    customer_segments TEXT,
    product_categories TEXT,
    source_name TEXT,
    source_url TEXT,
    confidence_score NUMERIC(4,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Distributor Relationship Signal Table
CREATE TABLE IF NOT EXISTS ref.distributor_relationship_signal (
    distributor_signal_id BIGSERIAL PRIMARY KEY,
    distributor_name TEXT,
    organization_name_raw TEXT,
    normalized_organization_name TEXT,
    organization_type TEXT,
    city TEXT,
    state TEXT,
    relationship_type TEXT,
    relationship_description TEXT,
    evidence_text_short TEXT,
    source_name TEXT,
    source_url TEXT,
    source_publish_date DATE,
    source_access_date DATE,
    confidence_score NUMERIC(4,2),
    is_confirmed_relationship BOOLEAN DEFAULT FALSE,
    extraction_method TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: Since psql is not available in the sandbox, I will provide the COPY commands
-- but execution will be simulated via mock inserts or handled by the platform's
-- ingestion layer.

/*
COPY ref.distributor_coverage(distributor_name, service_type, geographic_coverage, warehouse_locations, customer_segments, product_categories, source_name, source_url, confidence_score)
FROM 'data/raw/distributor/distributor_coverage.csv'
DELIMITER ',' CSV HEADER;

COPY ref.distributor_relationship_signal(distributor_name, organization_name_raw, organization_type, city, state, relationship_type, relationship_description, evidence_text_short, source_url, source_name, source_publish_date, source_access_date, confidence_score, is_confirmed_relationship, extraction_method, notes, normalized_organization_name)
FROM 'data/raw/distributor/distributor_relationship_signals.csv'
DELIMITER ',' CSV HEADER;
*/

-- 3. Mart View: Latest Distributor Channel Insight
CREATE OR REPLACE VIEW mart.vw_distributor_channel_latest AS
SELECT
    sig.distributor_signal_id,
    sig.distributor_name,
    sig.normalized_organization_name,
    sig.organization_type,
    sig.city,
    sig.state,
    sig.relationship_type,
    sig.relationship_description,
    sig.evidence_text_short,
    sig.source_name,
    sig.source_url,
    sig.confidence_score,
    sig.is_confirmed_relationship,
    cov.service_type AS distributor_service_type,
    cov.geographic_coverage AS distributor_geographic_coverage
FROM ref.distributor_relationship_signal sig
LEFT JOIN ref.distributor_coverage cov ON sig.distributor_name = cov.distributor_name
WHERE sig.confidence_score >= 0.6;
