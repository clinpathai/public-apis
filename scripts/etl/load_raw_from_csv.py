import pandas as pd
import os
import sys
from sqlalchemy import text
from .common import get_db_engine, log_pipeline_run, log_pipeline_step

def load_data(csv_path, table_name, schema='raw'):
    """Loads a CSV into PostgreSQL with full auditing and robust fallback."""
    pipeline_name = f"Load_{table_name}"
    engine = get_db_engine()

    df = None
    if os.path.exists(csv_path):
        print(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path)
    else:
        print(f"Error: {csv_path} not found.")
        return

    run_id = None
    try:
        run_id = log_pipeline_run(engine, pipeline_name, status='STARTED', details=f"Starting load of {csv_path}")
    except Exception as e:
        print(f"Auditing unavailable (DB down): {e}")

    try:
        if run_id:
            log_pipeline_step(engine, run_id, "Read CSV", status='SUCCESS')

        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            conn.commit()

        print(f"Loading into {schema}.{table_name}...")
        df.to_sql(table_name, engine, schema=schema, if_exists='replace', index=False)

        success_msg = f"Successfully loaded {len(df)} rows into {schema}.{table_name}"
        print(success_msg)
        if run_id:
            log_pipeline_step(engine, run_id, "To SQL", status='SUCCESS')
            log_pipeline_run(engine, pipeline_name, status='COMPLETED', details=success_msg)

    except Exception as e:
        error_msg = str(e)
        print(f"Database ingestion failed: {error_msg}")
        if run_id:
            log_pipeline_step(engine, run_id, "Database Ingestion", status='FAILED', error_msg=error_msg)

        # SQL Fallback
        try:
            sql_dir = "scripts/etl/sql_fallbacks"
            os.makedirs(sql_dir, exist_ok=True)
            sql_path = os.path.join(sql_dir, f"load_{table_name}.sql")
            print(f"Generating SQL fallback at {sql_path}...")
            with open(sql_path, 'w') as f:
                f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")
                cols = ", ".join([f"\"{col}\" TEXT" for col in df.columns])
                f.write(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} ({cols});\n")
                for _, row in df.iterrows():
                    val_list = []
                    for v in row.values:
                        escaped = str(v).replace("'", "''")
                        val_list.append(f"'{escaped}'")
                    vals = ", ".join(val_list)
                    f.write(f"INSERT INTO {schema}.{table_name} VALUES ({vals});\n")
            if run_id:
                log_pipeline_step(engine, run_id, "SQL Fallback Generation", status='SUCCESS')
                log_pipeline_run(engine, pipeline_name, status='COMPLETED_WITH_FALLBACK', details=f"Database failed, SQL generated at {sql_path}")
        except Exception as e2:
            print(f"Fallback generation failed: {e2}")
            if run_id:
                log_pipeline_run(engine, pipeline_name, status='CRITICAL_FAILURE', details=f"Database and fallback failed: {e2}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m scripts.etl.load_raw_from_csv <csv_path> <table_name> [schema]")
    else:
        csv_p = sys.argv[1]
        tbl_n = sys.argv[2]
        sch_n = sys.argv[3] if len(sys.argv) > 3 else 'raw'
        load_data(csv_p, tbl_n, sch_n)
