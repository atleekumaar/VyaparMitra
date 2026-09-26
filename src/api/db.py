import sqlite3
import pandas as pd
from src.api.config import get_api_config

def get_db_connection():
    config = get_api_config()
    conn = sqlite3.connect(config.db_path)
    # Return rows as dicts for easy access if needed, though pandas uses the raw connection
    return conn

def fetch_table_df(table_name: str) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        # Table might not exist yet
        return pd.DataFrame()
    finally:
        conn.close()
