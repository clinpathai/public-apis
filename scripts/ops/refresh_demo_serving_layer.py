import os
import sys
from sqlalchemy import text

# Add parent dir to path to import from etl.common
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from etl.common import get_db_engine

def refresh_views():
    sql = """
    CREATE SCHEMA IF NOT EXISTS mart;

    -- Snapshot of enriched 340B hospital pricing with pharmacy/distributor detail
    DROP MATERIALIZED VIEW IF EXISTS mart.mv_340b_channel_pricing_snapshot CASCADE;
    CREATE MATERIALIZED VIEW mart.mv_340b_channel_pricing_snapshot AS
    SELECT
        hospital_340b_id,
        hospital_name,
        ccn,
        contract_pharmacy_name,
        likely_distributor as distributor,
        billing_code as procedure_name,
        negotiated_rate,
        expiration_date
    FROM raw.hospital_340b_tic_mapping;

    -- Opportunity view for BD Discovery showing revenue potential per distributor/pharmacy network
    -- Note: Revenue is grouped by unique hospital-procedure to avoid Cartesian product duplication from pharmacies
    CREATE OR REPLACE VIEW mart.vw_channel_revenue_potential AS
    WITH hospital_pricing AS (
        SELECT DISTINCT hospital_name, distributor, billing_code, negotiated_rate
        FROM raw.hospital_340b_tic_mapping
    )
    SELECT
        distributor,
        COUNT(DISTINCT hospital_name) as hospital_count,
        SUM(CAST(negotiated_rate AS NUMERIC)) as total_negotiated_volume,
        RANK() OVER (ORDER BY SUM(CAST(negotiated_rate AS NUMERIC)) DESC) as market_share_rank
    FROM hospital_pricing
    GROUP BY distributor;

    -- Hospital level intelligence
    CREATE OR REPLACE VIEW mart.vw_hospital_intelligence AS
    SELECT
        hospital_name,
        hospital_340b_id,
        COUNT(DISTINCT contract_pharmacy_name) as active_contract_pharmacies,
        -- Weighted potential: sum of distinct procedure rates for this hospital
        (SELECT SUM(CAST(negotiated_rate AS NUMERIC))
         FROM (SELECT DISTINCT billing_code, negotiated_rate
               FROM raw.hospital_340b_tic_mapping inner_m
               WHERE inner_m.hospital_340b_id = outer_m.hospital_340b_id) as sub) as tic_revenue_potential
    FROM raw.hospital_340b_tic_mapping outer_m
    GROUP BY hospital_name, hospital_340b_id;
    """

    print("Refreshing demo serving layer with full pharmacy context...")
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

if __name__ == "__main__":
    refresh_views()
