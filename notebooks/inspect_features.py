"""
Quick interactive inspection script for VyaparMitra Phase 1 Feature Store.
"""

from pathlib import Path
import pandas as pd

FEATURES_DIR = Path("data/features")


def main():
    print("=== VYAPARMITRA FEATURE STORE INSPECTION ===")
    for parquet_file in sorted(FEATURES_DIR.glob("*.parquet")):
        df = pd.read_parquet(parquet_file)
        print(f"\n--- {parquet_file.name} ---")
        print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns[:8])}...")
        print(df.head(2))


if __name__ == "__main__":
    main()
