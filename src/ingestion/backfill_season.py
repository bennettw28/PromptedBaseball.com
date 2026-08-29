from pybaseball import statcast
from datetime import date, timedelta
import os

start = date(2026, 3, 25)  # 2026 opening night
end = date.today() - timedelta(days=1)

current = start
while current <= end:
    date_str = current.strftime('%Y-%m-%d')
    output_path = f"data/raw/statcast_{date_str}.csv"

    # skip days already pulled, makes this safe to stop and rerun
    if os.path.exists(output_path):
        print(f"already have {date_str}, skipping")
    else:
        data = statcast(start_dt=date_str, end_dt=date_str)
        data.to_csv(output_path, index=False)
        print(f"saved {len(data)} rows for {date_str}")

    current += timedelta(days=1)