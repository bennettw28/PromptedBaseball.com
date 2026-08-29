from pybaseball import playerid_lookup
import sqlite3
import pandas as pd

def innings_to_outs(ip):
    # innings pitched like 6.2 means 6 innings + 2 outs, not 6.2 decimal
    whole = int(ip)
    partial = round((ip - whole) * 10)
    return whole * 3 + partial

def get_pitcher_last_x_outings(last_name, first_name, x):
    lookup = playerid_lookup(last_name, first_name)
    player_id = lookup.iloc[0]['key_mlbam']  # takes first match, doesn't handle same-name conflicts yet

    conn = sqlite3.connect("data/promptedbaseball.db")
    df = pd.read_sql(
        "SELECT * FROM game_logs WHERE player_id = ? ORDER BY date",
        conn,
        params=(int(player_id),)
    )
    conn.close()

    recent = df.tail(x)

    wins = recent['wins'].sum()
    losses = recent['losses'].sum()

    total_outs = sum(innings_to_outs(ip) for ip in recent['innings_pitched'])
    total_er = recent['earned_runs'].sum()

    era = (total_er * 9) / (total_outs / 3)

    return wins, losses, round(era, 2)

def get_last_x_outings_by_id(player_id, x):
    conn = sqlite3.connect("data/promptedbaseball.db")
    df = pd.read_sql(
        "SELECT * FROM game_logs WHERE player_id = ? ORDER BY date",
        conn,
        params=(int(player_id),)
    )
    conn.close()

    recent = df.tail(x)
    actual_x = len(recent)

    wins = recent['wins'].sum()
    losses = recent['losses'].sum()

    total_outs = sum(innings_to_outs(ip) for ip in recent['innings_pitched'])
    total_er = recent['earned_runs'].sum()

    era = (total_er * 9) / (total_outs / 3)

    return wins, losses, round(era, 2), actual_x

def get_pitcher_list():
    conn = sqlite3.connect("data/promptedbaseball.db")
    df = pd.read_sql(
        "SELECT pitcher, player_name, game_date, home_team, away_team, inning_topbot FROM pitches",
        conn
    )
    conn.close()

    # top of inning = home team pitching, bottom = away team pitching
    df['team'] = df.apply(lambda r: r['home_team'] if r['inning_topbot'] == 'Top' else r['away_team'], axis=1)

    # keep each pitcher's most recent game, in case of a trade
    df = df.sort_values('game_date').drop_duplicates('pitcher', keep='last')

    return df[['pitcher', 'player_name', 'team']]

if __name__ == "__main__":
    wins, losses, era = get_pitcher_last_x_outings("webb", "logan", 10)
    print(f"{wins}-{losses} with a {era} ERA in his last 10 outings")