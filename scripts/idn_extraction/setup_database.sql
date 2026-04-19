
    CREATE SCHEMA IF NOT EXISTS ref;
    CREATE SCHEMA IF NOT EXISTS mart;

    DROP TABLE IF EXISTS ref.idn_organization_signal_map CASCADE;
    CREATE TABLE ref.idn_organization_signal_map (
        idn_signal_id BIGSERIAL PRIMARY KEY,
        hospital_name_raw TEXT,
        normalized_hospital_name TEXT,
        idn_name_raw TEXT,
        normalized_idn_name TEXT,
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
        is_confirmed_idn_member BOOLEAN DEFAULT FALSE,
        extraction_method TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE OR REPLACE VIEW mart.vw_idn_relationship_latest AS
    SELECT * FROM ref.idn_organization_signal_map;
