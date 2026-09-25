import requests
import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("data/promptedbaseball.db")
batter_ids = pd.read_sql("SELECT DISTINCT batter FROM pitches", conn)['batter'].tolist()
conn.close()

os.makedirs("data/raw/batter_game_logs", exist_ok=True)

for player_id in batter_ids:
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {"stats": "gameLog", "group": "hitting", "season": 2026}

    response = requests.get(url, params=params)
    data = response.json()

    if not data['stats'] or not data['stats'][0]['splits']:
        print(f"no hitting game log for {player_id}, skipping")
        continue

    rows = []
    for s in data['stats'][0]['splits']:
        rows.append({
            "player_id": player_id,
            "date": s['date'],
            "opponent": s['opponent']['name'],
            "hits": s['stat']['hits'],
            "at_bats": s['stat']['atBats'],
            "home_runs": s['stat']['homeRuns'],
            "walks": s['stat']['baseOnBalls'],
            "hit_by_pitch": s['stat']['hitByPitch'],
            "sac_flies": s['stat']['sacFlies'],
            "total_bases": s['stat']['totalBases'],
        })

    df = pd.DataFrame(rows)
    output_path = f"data/raw/batter_game_logs/{player_id}.csv"
    df.to_csv(output_path, index=False)
    print(f"saved {len(df)} games for {player_id}")