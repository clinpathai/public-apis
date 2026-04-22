import os
from sqlalchemy import create_engine

def get_db_engine():
    # Corrected path: point to project root config/database.env
    env_path = os.path.join(os.getcwd(), 'config/database.env')

    # Simple parser for .env
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
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
