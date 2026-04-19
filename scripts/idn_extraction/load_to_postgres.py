import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

def main():
    # Note: Assuming connection details based on the prompt's mention of aplus_health_intel
    # We will use a fallback or try to connect to the local postgres

    db_name = "aplus_health_intel"
    # Try to connect. If it fails, we will at least have the SQL script ready.

    csv_file = "data/raw/idn_public/idn_relationship_signals.csv"
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)

    # SQL to create schema and table
    create_sql = f"""
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
    """

    print("Connecting to database...")
    try:
        # Standard local connection for the sandbox
        engine = create_engine(f'postgresql://jules@localhost/{db_name}')

        with engine.connect() as conn:
            print("Creating schema and table...")
            # execute() takes a string or a text() object.
            # In sqlalchemy 2.0, we should use text()
            from sqlalchemy import text
            for statement in create_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()

            print("Loading data...")
            df.to_sql('idn_organization_signal_map', engine, schema='ref', if_exists='append', index=False)
            conn.commit()

        print("Database loading complete.")
    except Exception as e:
        print(f"Error connecting to or loading database: {e}")
        print("Generating SQL file for manual execution if needed...")
        with open("scripts/idn_extraction/setup_database.sql", "w") as f:
            f.write(create_sql)
        print("SQL file generated at scripts/idn_extraction/setup_database.sql")

if __name__ == "__main__":
    main()
