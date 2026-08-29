import sqlite3
import pandas as pd
import glob

conn = sqlite3.connect("data/promptedbaseball.db")

files = sorted(glob.glob("data/raw/statcast_*.csv"))

for file in files:
    df = pd.read_csv(file)
    df.to_sql("pitches", conn, if_exists="append", index=False)
    print(f"loaded {file}")

conn.close()