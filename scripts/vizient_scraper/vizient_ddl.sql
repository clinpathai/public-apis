-- Suggested PostgreSQL target tables for Vizient Public Relationship Signals

-- RAW schema for initial data load
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.vizient_public_relationship_signal_source (
    source_id BIGSERIAL PRIMARY KEY,
    source_name TEXT,
    source_url TEXT,
    source_publish_date DATE,
    source_access_date DATE,
    organization_name_raw TEXT NOT NULL,
    normalized_organization_name TEXT,
    organization_type TEXT,
    city TEXT,
    state TEXT,
    relationship_type TEXT,
    relationship_description TEXT,
    evidence_text_short TEXT,
    confidence_score NUMERIC(4,2),
    gpo_name TEXT DEFAULT 'Vizient',
    gpo_confidence NUMERIC(4,2),
    is_confirmed_gpo_member BOOLEAN DEFAULT FALSE,
    notes TEXT,
    extraction_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REF schema for evidence-based signals map
CREATE SCHEMA IF NOT EXISTS ref;
CREATE TABLE IF NOT EXISTS ref.gpo_organization_signal_map (
    gpo_signal_id BIGSERIAL PRIMARY KEY,
    gpo_name TEXT NOT NULL,
    organization_name_raw TEXT NOT NULL,
    normalized_organization_name TEXT,
    organization_type TEXT,
    city TEXT,
    state TEXT,
    relationship_type TEXT,
    relationship_description TEXT,
    source_name TEXT,
    source_url TEXT,
    source_publish_date DATE,
    source_access_date DATE,
    evidence_text_short TEXT,
    confidence_score NUMERIC(4,2),
    gpo_confidence NUMERIC(4,2),
    is_confirmed_gpo_member BOOLEAN DEFAULT FALSE,
    extraction_method TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MART schema for latest signal view
CREATE SCHEMA IF NOT EXISTS mart;
CREATE OR REPLACE VIEW mart.vw_gpo_vizient_signal_latest AS
SELECT DISTINCT ON (normalized_organization_name, city, state)
    gpo_signal_id,
    gpo_name,
    normalized_organization_name,
    organization_type,
    city,
    state,
    relationship_type,
    confidence_score,
    is_confirmed_gpo_member,
    source_url,
    source_access_date
FROM ref.gpo_organization_signal_map
WHERE gpo_name = 'Vizient'
ORDER BY normalized_organization_name, city, state, confidence_score DESC, source_access_date DESC;
