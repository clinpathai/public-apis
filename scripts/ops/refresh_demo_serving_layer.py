import os
import sys
from sqlalchemy import text

# Add parent dir to path to import from etl.common
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from etl.common import get_db_engine

def refresh_views():
    # We define the mart views based on the channel intelligence requirements
    sql = """
    CREATE SCHEMA IF NOT EXISTS mart;

    -- Snapshot of enriched 340B hospital pricing
    DROP MATERIALIZED VIEW IF EXISTS mart.mv_340b_channel_pricing_snapshot CASCADE;
    CREATE MATERIALIZED VIEW mart.mv_340b_channel_pricing_snapshot AS
    SELECT
        hospital_340b_id,
        hospital_name,
        ccn,
        billing_code as procedure_name,
        negotiated_rate,
        -- In a real mart, we would join with distributor logic here
        CASE
            WHEN hospital_name LIKE '%JOHNS HOPKINS%' THEN 'McKesson'
            WHEN hospital_name LIKE '%VANDERBILT%' THEN 'Cardinal Health'
            ELSE 'Unknown / Regional'
        END as primary_distributor
    FROM raw.hospital_340b_tic_mapping;

    -- Opportunity view for BD Discovery
    CREATE OR REPLACE VIEW mart.vw_idn_revenue_potential AS
    SELECT
        hospital_name,
        SUM(CAST(negotiated_rate AS NUMERIC)) as total_negotiated_volume,
        COUNT(DISTINCT billing_code) as procedure_count,
        RANK() OVER (ORDER BY SUM(CAST(negotiated_rate AS NUMERIC)) DESC) as opportunity_rank
    FROM raw.hospital_340b_tic_mapping
    GROUP BY hospital_name;
    """

    print("Refreshing demo serving layer...")
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            for statement in sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
        print("Mart layer refreshed successfully.")
    except Exception as e:
        print(f"Database refresh failed: {e}")
        with open("scripts/ops/mart_refresh_log.txt", "w") as f:
            f.write("Refresh failed. Falling back to static data for demo.\n")
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    refresh_views()
