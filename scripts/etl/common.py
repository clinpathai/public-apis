import os
import datetime
from sqlalchemy import create_engine, text

def get_db_engine():
    """Returns a SQLAlchemy engine based on config/database.env."""
    env_path = os.path.join(os.getcwd(), 'config/database.env')
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value

    db_name = config.get('DB_NAME', 'aplus_health_intel')
    db_user = config.get('DB_USER', 'jules')
    db_pass = config.get('DB_PASSWORD', '')
    db_host = config.get('DB_HOST', 'localhost')
    db_port = config.get('DB_PORT', '5432')

    password_part = f":{db_pass}" if db_pass else ""
    connection_url = f'postgresql://{db_user}{password_part}@{db_host}:{db_port}/{db_name}'
    return create_engine(connection_url)

def log_pipeline_run(engine, pipeline_name, status='STARTED', details=None):
    """Logs the start or completion of a pipeline run to ops.pipeline_run."""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ops;"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.pipeline_run (
                id SERIAL PRIMARY KEY,
                pipeline_name TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                details TEXT
            );
        """))

        if status == 'STARTED':
            result = conn.execute(text("""
                INSERT INTO ops.pipeline_run (pipeline_name, status, details)
                VALUES (:name, :status, :details) RETURNING id;
            """), {"name": pipeline_name, "status": status, "details": details})
            run_id = result.fetchone()[0]
            conn.commit()
            return run_id
        else:
            conn.execute(text("""
                UPDATE ops.pipeline_run SET status = :status, end_time = CURRENT_TIMESTAMP, details = :details
                WHERE pipeline_name = :name AND end_time IS NULL;
            """), {"status": status, "details": details, "name": pipeline_name})
            conn.commit()

def log_pipeline_step(engine, run_id, step_name, status='SUCCESS', error_msg=None):
    """Logs a specific step to ops.pipeline_step_log."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.pipeline_step_log (
                id SERIAL PRIMARY KEY,
                run_id INTEGER REFERENCES ops.pipeline_run(id),
                step_name TEXT,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text("""
            INSERT INTO ops.pipeline_step_log (run_id, step_name, status, error_message)
            VALUES (:run_id, :step_name, :status, :error);
        """), {"run_id": run_id, "step_name": step_name, "status": status, "error": error_msg})
        conn.commit()
