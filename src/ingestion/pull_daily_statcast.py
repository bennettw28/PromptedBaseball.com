from pybaseball import statcast
from datetime import date, timedelta
import sqlite3

# pull yesterday's games, today's might not be finalized yet
target_date = date.today() - timedelta(days=1)
target_date_str = target_date.strftime('%Y-%m-%d')

# get all statcast pitches for that date
data = statcast(start_dt=target_date_str, end_dt=target_date_str)

# save raw pull, one file per day
output_path = f"data/raw/statcast_{target_date_str}.csv"
data.to_csv(output_path, index=False)

# also add today's pitches to the master database
conn = sqlite3.connect("data/promptedbaseball.db")
data.to_sql("pitches", conn, if_exists="append", index=False)
conn.close()

print(f"saved {len(data)} rows to {output_path} and added to master db")