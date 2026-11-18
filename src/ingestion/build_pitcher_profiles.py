import sqlite3
import pandas as pd

DB_PATH = "data/promptedbaseball.db"

conn = sqlite3.connect(DB_PATH)
pitches = pd.read_sql("SELECT pitcher, pitch_type FROM pitches WHERE pitch_type IS NOT NULL", conn)

counts = pitches.groupby(["pitcher", "pitch_type"]).size().unstack(fill_value=0) #df 1 row per pitcher 1 col per pitch type
total = counts.sum(axis=1) #1 row per pitcher showing total pitches

usage = counts.div(total, axis=0).add_prefix("usage_") # add_prefix puts usage infront of every column name
usage["pitches_thrown"] = total #sets pitches thrown as total
usage = usage.reset_index() #turns pitcher_id from row name to just a regular column(numbers rows)

usage.to_sql("pitcher_profiles", conn, if_exists="replace", index=False)
conn.close()

print(f"built pitcher_profiles: {len(usage)} rows")