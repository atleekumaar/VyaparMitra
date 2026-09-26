import sqlite3
import pandas as pd
from src.api.config import get_api_config


def get_db_connection():
    config = get_api_config()
    conn = sqlite3.connect(config.db_path)
    return conn


def fetch_table_df(table_name: str) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def save_table_df(table_name: str, df: pd.DataFrame) -> None:
    conn = get_db_connection()
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    except Exception:
        pass
    finally:
        conn.close()
