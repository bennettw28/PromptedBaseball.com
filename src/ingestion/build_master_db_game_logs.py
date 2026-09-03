import sqlite3
import pandas as pd
import glob

conn = sqlite3.connect("data/promptedbaseball.db")

files = sorted(glob.glob("data/raw/game_logs/*.csv"))

for file in files:
    df = pd.read_csv(file)
    df.to_sql("game_logs", conn, if_exists="append", index=False)

conn.close()
print(f"loaded {len(files)} pitchers into game_logs table")