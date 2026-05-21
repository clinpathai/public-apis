import csv
import sys
import os
from common import get_db_connection, log_pipeline_run, log_pipeline_step, update_pipeline_status

def ingest_ortho_data(csv_file):
    pipeline_name = "Ortho_Independent_Powerhouses_Ingestion"
    conn = None
    run_id = None

    try:
        conn = get_db_connection()
        run_id = log_pipeline_run(conn, pipeline_name)
        log_pipeline_step(conn, run_id, "Read_CSV", "SUCCESS", f"Started processing {csv_file}")

        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        log_pipeline_step(conn, run_id, "Parse_Data", "SUCCESS", f"Parsed {len(rows)} records")

        with conn.cursor() as cur:
            for row in rows:
                # Map to core.company
                cur.execute("""
                    INSERT INTO core.company (name, state, website, ownership_model)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        state = EXCLUDED.state,
                        website = EXCLUDED.website,
                        ownership_model = EXCLUDED.ownership_model
                    RETURNING company_id
                """, (row['System_Name'], row['State'], '', row['Ownership_Model']))

                company_id = cur.fetchone()[0]

                # Map to core.bd_target
                cur.execute("""
                    INSERT INTO core.bd_target (company_id, primary_gatekeeper, clinical_focus, de_novo_activity, tech_adoption)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE SET
                        primary_gatekeeper = EXCLUDED.primary_gatekeeper,
                        clinical_focus = EXCLUDED.clinical_focus,
                        de_novo_activity = EXCLUDED.de_novo_activity,
                        tech_adoption = EXCLUDED.tech_adoption
                """, (company_id, row['Primary_Gatekeeper'], row['Clinical_Focus'], row['De_Novo_Activity'], row['Tech_Adoption']))

        conn.commit()
        log_pipeline_step(conn, run_id, "Database_Insert", "SUCCESS", "All records ingested and mapped")
        update_pipeline_status(conn, run_id, "COMPLETED")
        print(f"Successfully ingested {len(rows)} records into PostgreSQL.")

    except Exception as e:
        if conn:
            conn.rollback()
            if run_id:
                log_pipeline_step(conn, run_id, "Ingestion_Error", "FAILED", str(e))
                update_pipeline_status(conn, run_id, "FAILED")
        print(f"Error during ingestion: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    ingest_ortho_data('../../ortho_mso_intelligence.csv')
