import sqlite3
import pandas as pd

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

    # ops is cumulative per row like era was, so recalc from real totals rather than averaging the ops column
    obp_num = recent['hits'].sum() + recent['walks'].sum() + recent['hit_by_pitch'].sum()
    obp_denom = recent['at_bats'].sum() + recent['walks'].sum() + recent['hit_by_pitch'].sum() + recent['sac_flies'].sum()
    obp = obp_num / obp_denom if obp_denom > 0 else 0.0

    slg = recent['total_bases'].sum() / at_bats if at_bats > 0 else 0.0

    ops = round(obp + slg, 3)

    return hits, at_bats, avg, ops, home_runs, actual_x