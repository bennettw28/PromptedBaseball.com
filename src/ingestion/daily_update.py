from pybaseball import statcast
from datetime import date, timedelta
import pandas as pd
import sqlite3
import requests

DB_PATH = "data/promptedbaseball.db"

#11 sets target date as yesterday
#12 organizes the date into a string format that can be remembered and referenced later.
target_date = date.today() - timedelta(days=1)
target_date_str = target_date.strftime('%Y-%m-%d')

#16 sets the start and end date to yesterday so that it only pulls yesterdays data. statcast is a function of pybasebal that pulls pitch level data
#17 turn the pitch data that was just pulled into a csv named according to its date
pitch_data = statcast(start_dt=target_date_str, end_dt=target_date_str)
pitch_data.to_csv(f"data/raw/pitches_per_day/statcast_{target_date_str}.csv", index=False)

#20 opens the conenction to the db file allowing me to run sql functions
conn = sqlite3.connect(DB_PATH)

#25 runs through conn via conn.execute, this deletes every row where game_date matches yesterdays date in order to clean it up before re adding
#26 adds the pitch data from the day to the sql file that has all of the pitched
#27 saves everything done through conn since last comit
conn.execute("DELETE FROM pitches WHERE game_date = ?", (target_date_str,))
pitch_data.to_sql("pitches", conn, if_exists="append", index=False)
conn.commit()
print(f"updated pitches for {target_date_str}: {len(pitch_data)} rows")

#32 gets the pitcher id of distinct pitchers and puts them in a list
#33 wipes game logs
pitcher_ids = pd.read_sql("SELECT DISTINCT pitcher FROM pitches", conn)['pitcher'].tolist()
conn.execute("DELETE FROM game_logs")
conn.commit()


for player_id in pitcher_ids:
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats" 
    params = {"stats": "gameLog", "group": "pitching", "season": 2026}
    response = requests.get(url, params=params) #returns an object with json text
    data = response.json() #parses the json object into a python dict

    if not data['stats'] or not data['stats'][0]['splits']: #this skips rows where no games are logged
        continue

    rows = []
    for s in data['stats'][0]['splits']: #stats is a list, 0 is the first item which is a dict and splits is the key value of that dict, #s is one games dictionary
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
    df.to_csv(f"data/raw/game_logs/{player_id}.csv", index=False) #creates file for data 
    df.to_sql("game_logs", conn, if_exists="append", index=False) #game logs here is the table inside the db

print("refreshed game logs for all pitchers")

batter_ids = pd.read_sql("SELECT DISTINCT batter FROM pitches", conn)['batter'].tolist()
conn.execute("DELETE FROM batter_game_logs")
conn.commit()

for player_id in batter_ids:
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {"stats": "gameLog", "group": "hitting", "season": 2026}
    response = requests.get(url, params=params)
    data = response.json()

    if not data['stats'] or not data['stats'][0]['splits']:
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
    df.to_csv(f"data/raw/batter_game_logs/{player_id}.csv", index=False)
    df.to_sql("batter_game_logs", conn, if_exists="append", index=False)

print("refreshed game logs for all batters")

conn.close()
