import requests
import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("data/promptedbaseball.db")
pitcher_ids = pd.read_sql("SELECT DISTINCT pitcher FROM pitches", conn)['pitcher'].tolist()
conn.close()

os.makedirs("data/raw/game_logs", exist_ok=True)

for player_id in pitcher_ids:
    output_path = f"data/raw/game_logs/{player_id}.csv"

    # skip pitchers already pulled, same resumable pattern as the backfill script
    if os.path.exists(output_path):
        print(f"already have {player_id}, skipping")
        continue

    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {"stats": "gameLog", "group": "pitching", "season": 2026}

    response = requests.get(url, params=params)
    data = response.json()

    if not data['stats'] or not data['stats'][0]['splits']:
        print(f"no pitching game log for {player_id}, skipping")
        continue

    splits = data['stats'][0]['splits']

    rows = []
    for s in splits:
        rows.append({
            "player_id": player_id,
            "date": s['date'],
            "opponent": s['opponent']['name'],
            "is_win": s['isWin'],
            "wins": s['stat']['wins'],
            "losses": s['stat']['losses'],
            "era": s['stat']['era'],
            "innings_pitched": s['stat']['inningsPitched'],
            "earned_runs": s['stat']['earnedRuns'],
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"saved {len(df)} outings for {player_id}")