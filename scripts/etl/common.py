import os
import psycopg2
from datetime import datetime

def get_db_connection():
    # In a real environment, this would read from config/database.env
    # For the demo, we use placeholders or environment variables
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "aplus_health_intel"),
        user=os.getenv("DB_USER", "jules"),
        password=os.getenv("DB_PASSWORD", "")
    )

def log_pipeline_run(conn, pipeline_name):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ops.pipeline_run (pipeline_name, start_time, status) VALUES (%s, %s, %s) RETURNING run_id",
            (pipeline_name, datetime.now(), "RUNNING")
        )
        return cur.fetchone()[0]

def log_pipeline_step(conn, run_id, step_name, status, message=None):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ops.pipeline_step_log (run_id, step_name, status, message, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (run_id, step_name, status, message, datetime.now())
        )

def update_pipeline_status(conn, run_id, status):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE ops.pipeline_run SET status = %s, end_time = %s WHERE run_id = %s",
            (status, datetime.now(), run_id)
        )
