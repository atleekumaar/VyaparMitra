import os
import glob
import pandas as pd
import sqlite3
from pathlib import Path

def main():
    db_path = 'data/vyaparmitra.db'
    conn = sqlite3.connect(db_path)
    
    parquet_files = glob.glob('data/**/*.parquet', recursive=True)
    for pf in parquet_files:
        table_name = Path(pf).stem
        print(f"Loading {pf} into table {table_name}...")
        try:
            df = pd.read_parquet(pf)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        except Exception as e:
            print(f"Error loading {pf}: {e}")
            
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    main()
