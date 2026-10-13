import sqlite3
import pandas as pd
from pybaseball import playerid_reverse_lookup


def get_last_x_games_by_id(player_id, x):
    conn = sqlite3.connect("data/promptedbaseball.db")
    df = pd.read_sql(
        "SELECT * FROM batter_game_logs WHERE player_id = ? ORDER BY date",
        conn,
        params=(int(player_id),)
    )
    conn.close()

    recent = df.tail(x)
    actual_x = len(recent)

    hits = recent['hits'].sum()
    at_bats = recent['at_bats'].sum()
    home_runs = recent['home_runs'].sum()

    avg = round(hits / at_bats, 3) if at_bats > 0 else 0.0

    obp_num = recent['hits'].sum() + recent['walks'].sum() + recent['hit_by_pitch'].sum()
    obp_denom = recent['at_bats'].sum() + recent['walks'].sum() + recent['hit_by_pitch'].sum() + recent['sac_flies'].sum()
    obp = obp_num / obp_denom if obp_denom > 0 else 0.0

    slg = recent['total_bases'].sum() / at_bats if at_bats > 0 else 0.0

    ops = round(obp + slg, 3)

    return hits, at_bats, avg, ops, home_runs, actual_x
#this code first gets all of the games from this player, then gets the number x most recent ones, 
#uses this to calculate all the stats

def get_batter_list():
    conn = sqlite3.connect("data/promptedbaseball.db")
    df = pd.read_sql(
        "SELECT batter, game_date, home_team, away_team, inning_topbot FROM pitches",
        conn
    )
    conn.close()

    df['team'] = df.apply(lambda r: r['away_team'] if r['inning_topbot'] == 'Top' else r['home_team'], axis=1) 
#this just sets team as the away team if is the top of the inning and the home team if not, it is creating a new column.

    df = df.sort_values('game_date').drop_duplicates('batter', keep='last')
#drops duplicates so the dropdown only has one of each player, keeps last so its his most recent team.

    names = playerid_reverse_lookup(df['batter'].tolist(), key_type='mlbam') #uses player id's to get names, func returns a df
    df = df.merge(names[['key_mlbam', 'name_first', 'name_last']], left_on='batter', right_on='key_mlbam')

    return df[['batter', 'name_first', 'name_last', 'team']]

if __name__ == "__main__":
    hits, at_bats, avg, ops, home_runs, actual_x = get_last_x_games_by_id(514888, 10)
    print(f"{hits} for {at_bats} ({avg}) with a {ops} OPS and {home_runs} home runs in his last {actual_x} games")
# if name == "__main__": only runs this test if this file is the one being ran

#this file calculates a batters stats over his last x games and creates the list of batters.