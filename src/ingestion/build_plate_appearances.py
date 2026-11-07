import sqlite3
import pandas as pd

DB_PATH = "data/promptedbaseball.db"

conn = sqlite3.connect(DB_PATH)
pitches = pd.read_sql("SELECT * FROM pitches", conn)

pitches = pitches.sort_values(["game_date", "game_pk", "at_bat_number", "pitch_number"])

last_pitch = pitches.groupby(["game_pk", "at_bat_number"]).tail(1)

pa = last_pitch.copy()
pa["pitches_in_pa"] = pa["pitch_number"]

pa = pa[["game_pk", "at_bat_number", "game_date", "game_type", "batter", "pitcher", "stand", "p_throws",
         "home_team", "away_team", "inning", "inning_topbot", "outs_when_up", "on_1b", "on_2b", "on_3b",
         "home_score", "away_score", "events", "pitches_in_pa", "pitch_type", "release_speed"]]

pa = pa.rename(columns={"pitch_type": "final_pitch_type", "release_speed": "final_pitch_mph"})

pa["batting_team"] = pa["home_team"].where(pa["inning_topbot"] == "Bot", pa["away_team"])
pa["pitching_team"] = pa["away_team"].where(pa["inning_topbot"] == "Bot", pa["home_team"])

pa["on_1b"] = pa["on_1b"].notna().astype(int)
pa["on_2b"] = pa["on_2b"].notna().astype(int)
pa["on_3b"] = pa["on_3b"].notna().astype(int)

def make_bases(row):
    occupied = []
    if row["on_1b"] == 1:
        occupied.append("1B")
    if row["on_2b"] == 1:
        occupied.append("2B")
    if row["on_3b"] == 1:
        occupied.append("3B")
    if not occupied:
        return "empty"
    return "_".join(occupied)

pa["bases"] = pa.apply(make_bases, axis=1)

hit_events = ["single", "double", "triple", "home_run"]
walk_events = ["walk", "intent_walk"]
sac_fly_events = ["sac_fly", "sac_fly_double_play"]
no_ab_events = walk_events + sac_fly_events + ["hit_by_pitch", "sac_bunt", "sac_bunt_double_play", "catcher_interf"]
bases_map = {"single": 1, "double": 2, "triple": 3, "home_run": 4}

pa["is_hit"] = pa["events"].isin(hit_events).astype(int)
pa["is_hr"] = (pa["events"] == "home_run").astype(int)
pa["is_walk"] = pa["events"].isin(walk_events).astype(int)
pa["is_hbp"] = (pa["events"] == "hit_by_pitch").astype(int)
pa["is_sac_fly"] = pa["events"].isin(sac_fly_events).astype(int)
pa["is_ab"] = (~pa["events"].isin(no_ab_events)).astype(int)
pa["total_bases"] = pa["events"].map(bases_map).fillna(0).astype(int)

non_pa_events = ["caught_stealing_2b", "caught_stealing_3b", "caught_stealing_home",
                 "pickoff_1b", "pickoff_2b", "pickoff_3b",
                 "pickoff_caught_stealing_2b", "pickoff_caught_stealing_3b", "pickoff_caught_stealing_home",
                 "truncated_pa"]

pa = pa[pa["events"].notna() & ~pa["events"].isin(non_pa_events)] #keeps: is an even and not(~) in non_pa events 

pa["is_home"] = (pa["inning_topbot"] == "Bot").astype(int)

pa.to_sql("plate_appearances", conn, if_exists="replace", index=False)
conn.close()

print(f"built plate_appearances: {len(pa)} rows")