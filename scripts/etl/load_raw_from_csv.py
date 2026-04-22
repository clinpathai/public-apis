import pandas as pd
import os
from sqlalchemy import text
from .common import get_db_engine

def load_data(csv_path, table_name, schema='raw'):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Loading {csv_path} into {schema}.{table_name}...")
    df = pd.read_csv(csv_path)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            conn.commit()

            df.to_sql(table_name, engine, schema=schema, if_exists='replace', index=False)
            print(f"Successfully loaded {len(df)} rows into {schema}.{table_name}")
    except Exception as e:
        print(f"Database connection failed: {e}")
        # Generate SQL as fallback
        sql_path = f"scripts/etl/load_{table_name}.sql"
        print(f"Generating SQL fallback at {sql_path}...")
        with open(sql_path, 'w') as f:
            f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")
            cols = ", ".join([f"{col} TEXT" for col in df.columns])
            f.write(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} ({cols});\n")
            for _, row in df.iterrows():
                # Fixed syntax error: avoiding nested quotes issue in f-strings
                val_list = []
                for v in row.values:
                    escaped = str(v).replace("'", "''")
                    val_list.append(f"'{escaped}'")
                vals = ", ".join(val_list)
                f.write(f"INSERT INTO {schema}.{table_name} VALUES ({vals});\n")
        print("SQL fallback generation complete.")

if __name__ == "__main__":
    target_file = "data/processed/enriched_hospital_mapping.csv"
    source_file = "data/processed/tic_hospital_rates_enriched.csv"

    if os.path.exists(source_file) and not os.path.exists(target_file):
        import shutil
        shutil.copy(source_file, target_file)

    load_data(target_file, "hospital_340b_tic_mapping")
